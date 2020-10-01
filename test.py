import unittest
from spot import Fetcher, spot
import os

#My own logs. I would call myself familiar with them. There's something like 2.5k
Zidgel = spot.GET_IDs("76561198098770013")
zfetcher = Fetcher(skip_init = True, save_directory = os.path.join("Z:\log_dumps", str(Zidgel['64'])))
ZidgelLogs = zfetcher.from_dir(sort=True)

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
