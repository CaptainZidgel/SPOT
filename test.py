import unittest
from spot import Fetcher, spot
import os

#My own logs. I would call myself familiar with them. There's something like 2.5k
Zidgel = spot.GET_IDs("76561198098770013")
zfetcher = Fetcher(skip_init = True, save_directory = os.path.join("Z:\log_dumps", str(Zidgel['64'])))
ZidgelLogs = zfetcher.from_dir(sort=True)

#My sincerest apologies to anyone reading this.
sample_ids_med_dict = {"T": {2678678, 2678666, 2678653, 2676716, 2676707}, "F": {2678635, 2676699, 2669814, 2669789, 2669775, 2668817}} #ismedic, notismedic
sample_ids_med = sample_ids_med_dict["T"] | sample_ids_med_dict["F"]
samplelogs_med = zfetcher.from_dir(select=sample_ids_med)

#I once downloaded Habib's 8k logs to compare with another player, logs date back to 2013 so he seems like a good pool of logs to use.
Habib = spot.GET_IDs("76561198053621664")
hfetcher = Fetcher(skip_init = True, save_directory = os.path.join("Z:\log_dumps", str(Habib['64'])))
HabibLogs = hfetcher.from_dir(sort=True, limit=150)

zext = spot.Extract(Zidgel)
hext = spot.Extract(Habib)
combexit = spot.Extract(Zidgel, Habib) #The use case of this is for combining user alts, but ...

class TestIDExtract(unittest.TestCase):
    def test_get_id(self): #Test some GET_ID cases
        self.assertEqual(spot.GET_IDs("https://steamcommunity.com/profiles/76561198098770013"), spot.GET_IDs("76561198098770013"))
        self.assertEqual(spot.GET_IDs("76561198098770013"), spot.GET_IDs(76561198098770013))
        self.assertRaises(spot.BadID, spot.GET_IDs, "HI MOM")
    
    def test_get_from3_singular(self): #test you can get a steam3 from my log
        self.assertEqual(zext.ID(ZidgelLogs[1]), Zidgel['3'])
        
    def test_get_from3_with_multiple_choice(self): #The function must find habib3 or zidgel3 from these logs.
        self.assertEqual(combexit.ID(ZidgelLogs[0]), Zidgel['3'])
        self.assertEqual(combexit.ID(HabibLogs[100]), Habib['3'])

    def test_get_from1(self): #test you can compare the log's steam_0 to the steam.steamid's steam_1
        self.assertEqual(hext.ID(HabibLogs[0]), Habib['1a'])

    def test_usernotfound(self):
        self.assertRaises(spot.UserNotPresent, zext.ID, HabibLogs[0]) #I am definitely not in whatever this log is

class TestFilters(unittest.TestCase):
    def test_no_medic(self):
        ap = spot.Approver()
        ap._config(samplelogs_med, zext)
        ap._do(spot.PLAYEDHALF, filters={"medic"})
        self.assertCountEqual(sample_ids_med_dict["F"], [int(l["id"]) for l in ap.logs])

    def test_yes_medic(self):
        ap = spot.Approver()
        ap._config(samplelogs_med, zext)
        ap._do(spot.PLAYEDHALF, filters={"combat"})
        self.assertCountEqual(sample_ids_med_dict["T"], [int(l["id"]) for l in ap.logs])
