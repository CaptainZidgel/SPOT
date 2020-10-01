import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean
from steam.steamid import SteamID
from datetime import datetime
from .tf2seasons import tf2seasons

class UserNotPresent(Exception):
    pass

class BadID(Exception):
    pass

def _genAlt(steam1):
    '''
    From the Steam Devs Wiki: https://developer.valvesoftware.com/wiki/SteamID
    The value of X is 0 in VALVe's GoldSrc and Source Orange Box Engine games (For example, Counter Strike: Source), but newer Valve games such as Left 4 Dead, Left 4 Dead 2 and Alien Swarm have 1 as a value of X.
    X being STEAM_X:Y:1234567...
    I do not comprehend this issue, how can games affect a registration ID? Either way, your average conversion module like `steam.steamid` is going to give you a STEAM_1:Y. BAD!
    '''
    if steam1[6] == '0':
        return steam1.replace("_0", "_1")
    elif steam1[6] == '1': #I don't know if this is ever a case but lets do it in the reverse way just in case!
        return steam1.replace("_1", "_0")

def GET_IDs(profile):
    """
    steam.steamid doesn't actually have exceptions!!!
    """
    steam64 = None
    if str(profile)[0] == 'h': #link
        steam64 = SteamID.from_url(profile).as_64
    elif str(profile)[0] == '7': #simply a pasted steam64
        steam64 = SteamID(profile)
    else:
        raise BadID("Don't recognize this ID. Pass a steam64 or a community profile link")
    if steam64 == None or isinstance(steam64, SteamID) and steam64.type == "Invalid":
        raise BadID("Don't recognize this ID. Is it a valid profile? (Pass profile link or steam64)")
    steam64 = int(steam64)
    steam3 = SteamID(steam64).as_steam3
    steam1 = SteamID(steam64).as_steam2
    alt = _genAlt(steam1)
    return {'64': steam64, '3': steam3, '1': steam1, '1a': alt}

tf2seasons = tf2seasons()
def GET_SEASON(identifier, key=None):
    for label, s in tf2seasons.all_seasons.items():
        if label == identifier:
            if key == None:
                return s['start'], s['end']
            else:
                return s[key]

def Alias(alias): #https://stackoverflow.com/questions/10874432/possible-to-change-function-name-in-definition
    def decorator(f):
        f.__name__ = alias
        return f
    return decorator

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
    def __init__(self, IDs, plotter, timeCondition, filters={'short', 'dupes', 'non6s', 'medic'}, doLog=True, dont=False):
        self.steam3 = IDs['3']
        self.steam1 = IDs['1']
        self.doLog = doLog
        self.plotter = plotter
        if dont: #dont is included as an option so you can access util functions yourself.
            return
        self.E = Extract(IDs)
        self.logs = self.plotter.r_logs
        print("Approver beginning inspection {}".format(len(self.logs))) if self.doLog else ''
        if 'short' in filters:
            self.FilterShortGames(600)
        if 'dupes' in filters:
            self.r = TimeRanges()
            self.FilterDupes()
        if 'non6s' in filters:
            self.FilterInvalid()
        if 'medic' in filters:
            self.FilterMedic()
        if not 'SAVE_funky_logs' in filters: #I get that this is a little odd but its not a real usecase, more of a debug thing.
            self.FilterExplicitlyLackDmg()
        self.FilterTimecond(timeCondition)

    def Finalize(self):
        self.plotter.logs = sorted(self.logs, key=lambda l: l['info']['date'])
        
    ########################IN-PLACE SELF.LOGS FILTERING###################
    def FilterShortGames(self, period):
        self.logs = [l for l in self.logs if l['info']['total_length'] > period] #filter out short games | NOTE: l['length'] exists in MOST logs, but I've run into problems in older logs, and afaik ['info']['total_length'] is in all logs.
        print("Approver filtering out short games... {}".format(len(self.logs))) if self.doLog else ''
    def FilterDupes(self):
        self.logs = self.r.verify_logs(self.logs)    #filter out dupes
        print("Approver filtering out dupes... {}".format(len(self.logs))) if self.doLog else ''
    def FilterInvalid(self):
        self.logs = [l for l in self.logs if self.InvalidFormat(l) == False] #filter out non-6s?
        print("Approver filtering out non 6s games... {}".format(len(self.logs))) if self.doLog else ''
    def FilterMedic(self):
        self.logs = [l for l in self.logs if self.IsClass(l, 'medic', 70) == False]
        print("Approver filtering out medic games... {}".format(len(self.logs))) if self.doLog else ''
    def FilterExplicitlyLackDmg(self):
        self.logs = [l for l in self.logs if self.UsefulLog(l)]
        print("Approver filtering out logs we can find that explictly lack useful information (usually old games) (this is a basic filter with no false positives, but many false negatives).. {}".format(len(self.logs))) if self.doLog else ''
    def FilterTimecond(self, timeCondition):
        if timeCondition == PLAYEDHALF:
            self.logs = [l for l in self.logs if self.GetPlayedTime(l) > l['info']['total_length'] / 2]
            print("Approver filtering out games with less than half playtime... {}".format(len(self.logs))) if self.doLog else ''
        elif timeCondition == PLAYEDFULL:
            self.logs = [l for l in self.logs if self.GetPlayedTime(l) == l['info']['total_length']]
            print("Approver filtering out games with less than full playtime... {}".format(len(self.logs))) if self.doLog else ''

    #Util########Util functions take 1 log each, so you can access and write your own loops####
    def GetPlayedTime(self, log):
        total = 0
        for classes in log['players'][self.E.ID(log)]['class_stats']:
                total += classes['total_time']
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

    def IsClass(self, log, myclass, percent_margin):
        cs = log['players'][self.E.ID(log)]['class_stats']
        if len(cs) == 1 and cs[0]['type'] == myclass:
            return True
        time = 0
        for _class in log['players'][self.E.ID(log)]['class_stats']:
            if _class['type'] == myclass:
                time += _class['total_time']
        if time > self.GetPlayedTime(log) * (percent_margin/100): #Played this class at least x% of the time
            return True
        return False

    def UsefulLog(self, log):
        try:
            if log['info']['hasRealDamage']:
                return True
            else:
                return False
        except KeyError:
            return True #Old logs that include dpm lack an indicator

    def Custom(self, func):
        self.logs = [l for l in self.logs if func(l)]
        print("Applying user-provided filter function: Length now: {}".format(len(self.logs))) if self.doLog else ''

class Extract:
    """
    Extract information from a log, based on a user's IDs (logs use multiple ID types across very long periods of time)
    Supports combining alts gracefully, if you were interested in that for some reason.
    Create as: e = spot.Extract(id_dictionary1)
    These id_dictionaries come from spot.GET_IDs and are a var arg: e = spot.Extract(id_dict1, id_dict2)
    """
    def __init__(self, *id_sets):
        self.ids = [{k:v for (k, v) in s.items()} for s in id_sets]
        self.types = ["3", "1", "1a"] #steam64s arent used for player identification in logs

    def ID(self, log):
        '''
        Get the ID to use for this log. (Current logs use Steam3, old logs use Steam1, some Steam1s have funky problems)
        This uses a lot of list comps and is incomprehensible but a lot smoother IMO than the IF chain I was using before,
        and it allows alt inclusion without recursion
        '''
        all_ids = [s[t] for t in self.types for s in self.ids] #Creates a list of ids in order of precedence, with alts accounted for. example where A and B are multiple accounts: [a3, b3, a1, b1, a1a, b1a]
        try:
            id_in = next((_id for _id in all_ids if _id in log["players"])) #Return the first (and only) ID to be in the log.
            return id_in
        except StopIteration: #this means next() failed because nothing was generated
            raise UserNotPresent(
                "Missing user {} in log {}. If you believe this is an error, please include this line in an error report, with the following information: [ {} ;; {} ]".format(
                    self.ids[0]['64'], log['id'], self.ids, all_ids
                ))
                    
    ##These aliased functions will get the data from ONE log, to be returned for processing in a loop. This is fine in most cases.
    @Alias("DPM")
    def DPM(self, log):
        return log['players'][self.ID(log)]['dapm']
    
    @Alias("Scout DPM")
    def DPM_SCOUT(self, log):
        for classes in log['players'][self.ID(log)]['class_stats']:
            if classes['type'] == 'scout':
                return classes['dmg'] / (classes['total_time'] / 60)

    @Alias("Soldier DPM")
    def DPM_SOLDIER(self, log):
        for classes in log['players'][self.ID(log)]['class_stats']:
            if classes['type'] == 'soldier':
                return classes['dmg'] / (classes['total_time'] / 60)
    
    @Alias("Demo DPM")
    def DPM_DEMO(self, log):
        for classes in log['players'][self.ID(log)]['class_stats']:
            if classes['type'] == 'demoman':
                return classes['dmg'] / (classes['total_time'] / 60)

    @Alias("Win%")
    def WIN(self, log):
        j = log
        me = self.ID(log)
        if j['teams']['Red']['score'] > j['teams']['Blue']['score'] and j['players'][me]['team'] == "Red":
          return 1
        elif j['teams']['Red']['score'] < j['teams']['Blue']['score'] and j['players'][me]['team'] == "Blue":
          return 1
        else:
          return 0

    @Alias("Kill/Death")
    def KD(self, log):
        return float(log['players'][self.ID(log)]['kpd'])

    def Stat_List(self, stat, collection):
        return [stat(l) for l in collection]

class Plotter:
    def __init__(self, logs):
        self.r_logs = logs #This stays static, in case you want to start over.
        self.logs = self.r_logs #This will be filled by approver

        logs = sorted(self.logs, key=lambda l: l['info']['date'])
        self.first = datetime.fromtimestamp(logs[0]['info']['date'])
        self.last = datetime.fromtimestamp(logs[-1]['info']['date'])

    def get_timestamped_values(self, stat, start=datetime(year=2000, month=1, day=1), end=datetime(year=3000, month=1, day=1)):
        '''
        Returns a pandas DatetimeIndexed Dataframe
        '''
        date_list = []
        val_list = []
        id_list = []
        for l in self.logs:
            t = datetime.fromtimestamp(l['info']['date'])
            if start <= t <= end:
                date_list.append(pd.to_datetime(l['info']['date'], unit="s"))
                val_list.append(stat(l))
                id_list.append(str(l['id']))
        dic = {'date': date_list, 'val': val_list, 'id': id_list}
        #dic = {'date': [pd.to_datetime(l['info']['date'], unit="s") for l in self.logs], 'val': [stat(l) for l in self.logs], "id": [str(l['id']) for l in self.logs]}
        #Creating a 1 dimensional dictionary here to convert to a dataframe. | NOTE: pd_to_datetime(blah, unit="s") ... blah is already a timestamp but pandas uses pseudo-typing or something so I'm converting it to a stamp, unit="s" means seconds. Don't know if that means unit as an input or as an output.
        df = pd.DataFrame({k: v for k, v in dic.items() if not k == "date"},
                          index = dic["date"])
        #Creating the actual dataframe from the dictionary, using date as an index.
        return df

    def resample(self, values, method="mean", period='W'):
        if method.lower() == "mean":
            return values.val.resample(period).mean()
        elif method.lower() == "sum":
            return values.val.resample(period).sum()
        else:
            raise Exception("[SPOT] Resample Method must be mean or sum")

    def shade_seasons(self, *axes, doText=True):
        for ax in axes:
            for lab, s in tf2seasons.all_seasons.items():
                if self.first <= s['start'] <= self.last or self.first <= s['end'] <= self.last:
                    ax.axvspan(s['start'], s['end'], alpha=0.1, color="gray")
                    if doText:
                        ax.text(s['start'], ax.get_ylim()[0], lab, rotation=90, fontsize='small')

    def set_xbounds(self, ax, bounds):
        if bounds == None:
            ax.set_xlim(left=self.first, right=self.last)
        else:
            if bounds[0]:
                self.first = bounds[0]
            if bounds[1]:
                self.last = bounds[1]
            ax.set_xlim(left=min(self.first, self.last), right=max(self.first, self.last))

    def normalize_ybounds(self, *axes, margins=5, bot=None, top=None):
        uppers = [a.get_ylim()[1] for a in axes]
        lowers = [a.get_ylim()[0] for a in axes]
        if not bot:
            bot = max(lowers)-margins
        if not top:
            top = max(uppers)+margins
        for ax in axes:
            ax.set_ylim(bottom=bot, top=top)
                
    def plot(self, stat, bounds=None, method="mean", period="weekly", shade_seasons=False):
        '''
        Creates a basic graph.
        Stat is the stat from class Extract you would like to graph.
        Bounds is the start/end of the graph. If not None, must be a tuple of datetimes, either (Start, End) or (None, datetime)
        Method is mean or sum, used to resample.
        Period is weekly or monthly.
        shade_seasons will shade in TF2 seasons.
        '''
        assert period == "weekly" or period == "monthly"
        vals = self.get_timestamped_values(stat)
        resamp = self.resample(vals, method=method, period=period[0])
        
        fig, ax1 = plt.subplots()
        ax1.plot(resamp.index, resamp)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("{} {} {}".format(method, period, stat.__name__))
        self.set_bounds(ax1, bounds)
        if shade_seasons:
            self.shade_seasons(ax1)

        plt.show()
