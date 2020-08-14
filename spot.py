import logfetch
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean

offclasses = {"pyro", "spy", "sniper", "engineer", "heavyweapons"}

class TimeRanges:
    def __init__(self):
        self.ranges = set()

    def PlusMinus(self, one, two, within):
        if abs(two - one) <= within:
            return True
        return False

    def checkOK(self, t):
        for time in self.ranges:
            if self.PlusMinus(t, time, 15):
                return False
        return True

    def verify_logs(self, logs):
        for l in logs:
            t = l['info']['date']
            if t not in self.ranges and self.checkOK(t):
                self.ranges.add(t)
        return [l for l in logs if l['info']['date'] in self.ranges]

PLAYEDHALF = 0
PLAYEDFULL = 1
class Approver:
    def __init__(self, logs, steamID3, timeCondition):
        self.player = steamID3
        self.r = TimeRanges()
        print("Approver beginning inspection {}".format(len(logs)))
        self.logs = self.r.verify_logs(logs)    #filter out dupes
        print("Approver filtering out dupes... {}".format(len(self.logs)))
        self.logs = [l for l in self.logs if l['length'] > 600] #filter out short games
        print("Approver filtering out short games... {}".format(len(self.logs)))
        self.logs = [l for l in self.logs if self.InvalidFormat(l) == False] #filter out non-6s?
        print("Approver filtering out non 6s games... {}".format(len(self.logs)))
        self.logs = [l for l in self.logs if self.IsMedic(l) == False]
        print("Approver filtering out medic games... {}".format(len(self.logs)))
        self.logs = [l for l in self.logs if self.UsefulLog(l)]
        print("Approver filtering out crappy logs.. {}".format(len(self.logs)))
        if timeCondition == PLAYEDHALF:
            self.logs = [l for l in self.logs if self.GetPlayedTime(l) > l['length'] / 2]
            print("Approver filtering out games with less than half playtime... {}".format(len(self.logs)))
        elif timeCondition == PLAYEDFULL:
            self.logs = [l for l in self.logs if self.GetPlayedTime(l) == l['length']]
            print("Approver filtering out games with less than full playtime... {}".format(len(self.logs)))
        
    def Result(self):
        return self.logs

    def GetPlayedTime(self, log):
        total = 0
        for classes in log['players'][self.player]['class_stats']:
            try:
                total += classes['total_time']
            except KeyError:
                pass
        return total

    def DetermineFormatFromOffclasses(self, log):
        '''
        Called from the InvalidFormat func as a last resort: If at least one person on each team
        fulltime offclassed, ignore this game
        '''
        Guilty_Teams = set()
        for _,player in log['players'].items():
            offclass_time = 0
            for classes in player['class_stats']:
                if classes['type'] in offclasses:
                    offclass_time += classes['total_time']
                    if len(classes) == 1 and offclass_time == l['length']:
                        Guilty_Teams.add(player['team'])
        if len(Guilty_Teams) == 2:
            return True
        return False

    def InvalidFormat(self, log, p=False):
        '''
        Returns True if NOT a sixes game,
        determines this by: Map, map type, player count, offclass shenanigans.
        '''
        sixes_koth = {"product", "clearcut", "bagel"}
        not_sixes_modes = {"pl", "ultiduo", "bball"}
        if log['info']['map'] == '':
            print("Map error (No map name)") if p else ''
            return True #Not an invalid game format, but an invalid log - probably a combined log
        mode = log['info']['map'].split("_")[0]  #>cp<_process_final
        try:
            map = log['info']['map'].split("_")[1]   #koth_>clearcut<_b15c
        except IndexError:
            print("Map error (Couldn't determine map name): ", map) if p else ''
            return True 
        if mode in not_sixes_modes:
            print("Not sixes mode", mode) if p else ''
            return True
        if len(log['players']) == 12 and (mode == "cp" or map in sixes_koth):
            print("Ideal conditions for 6s") if p else ''
            return False #The best case scenario: Exactly 12 players, on what is absolutely a 6s map.
        if len(log['players']) < 11 or len(log['players']) >= 18:
            print("Player count suggests not 6s") if p else ''
            return True #Ultiduo, Bball, 4s or HL. (if your 6s game had 18 players counted in logs because you had 6 subs, I don't know what to tell you.)
        if mode == "koth" and map not in sixes_koth and len(log['players']) >= 14:
            print("Probably prolander") if p else ''
            return True #Probably Prolander
        if self.DetermineFormatFromOffclasses(log):  #This function isn't definitive, which is why it comes last.
            print("Someone offclassed long enough to be considered HL") if p else ''
            return True #Someone was offclassing way too long. Has to be HL or Prolander.
        print("Can't find anything wrong. Likely 6s") if p else ''
        return False #Likely 6s

    def IsMedic(self, log):
        cs = ''
        try:
            cs = log['players'][self.player]['class_stats']
        except KeyError:
            print("[SPOT] Error... cannot find stats for you in this log {} <THAT MEANS IT COULD BE USING STEAM_1 FOR IDENTIFICATION. I DO NOT SUPPORT THIS, IF THIS HAPPENS FOR A LOT OF YOUR LOGS THEN REPORT IT AND I WILL TAKE CARE OF IT".format(log["id"]))
            return
        if len(cs) == 1 and cs[0]['type'] == 'medic':
            return True
        time = 0
        for _class in log['players'][self.player]['class_stats']:
            if _class['type'] == 'medic':
                time += _class['total_time']
        if time > 200:
            return True
        return False

    def UsefulLog(self, log):
        if log['info']['hasRealDamage']:
            return True
        else:
            return False

class Analyze:
    def __init__(self, logs, steamid3, tc):
        self.r_logs = logs
        self.player = steamid3
        self.APPROVER = Approver(logs, self.player, tc)
        self.DPMdict = lambda log: {log['id']: log['players'][self.player]['dapm']}
        self.DPMtup = lambda log: (log['id'], log['players'][self.player]['dapm'])
        self.DPM = lambda log: log['players'][self.player]['dapm']
        self.AVGDPM = lambda log: mean(self.DPM(log))
        self.logs = self.APPROVER.Result()

    def get_timerange(self):
        return [d['info']['date'] for d in logs if d['length'] > 600 and d['players'][self.player]['dapm'] > 100]

    def get_timestamped_values(self, stat):
        '''
        Returns a pandas DatetimeIndexed Dataframe
        '''
        dic = {'date': [pd.to_datetime(l['info']['date'], unit="s") for l in self.logs], 'val': [stat(l) for l in self.logs], "id": [str(l['id']) for l in self.logs]}
        #Creating a 1 dimensional dictionary here to convert to a dataframe. | NOTE: pd_to_datetime(blah, unit="s") ... blah is already a timestamp but pandas uses pseudo-typing or something so I'm converting it to a stamp, unit="s" means seconds. Don't know if that means unit as an input or as an output.
        df = pd.DataFrame({k: v for k, v in dic.items() if not k == "date"},
                          index = dic["date"])
        #Creating the actual dataframe from the dictionary, using date as an index.
        return df

    def resample(self, values, period='W'):
        return values.val.resample(period).mean()


