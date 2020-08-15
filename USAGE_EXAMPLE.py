import logfetch
import spot
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

IDs = spot.GET_IDs('Steam64 or profile link') #76561198098770013 -> Zidg

print("Fetching")
fetcher = logfetch.Fetcher('file', IDs['64'], skip_init=False, save_directory="dump/yourname")
logs = fetcher.fetch(do_progress_bar=False, do_file_return=True)

print("Analyzing")
e = spot.Extract(IDs)
p = spot.Plotter(logs)
approver = spot.Approver(IDs, p, spot.PLAYEDFULL, doLog=False)
approver.Finalize()

p.plot(e.DPM, method="mean", period="weekly", shade_seasons=True)


'''
for manually plotting, get x,y values like this: (this is not the comprehensive code you would write for matplotlib, this is a partial example for those who understand it)
dpm = plotter.get_timestamped_values(e.DPM, start=datetime(year=2020, month=1, day=1))
scoutweeklydpm = a.resample(dpm)
ax1.plot(scoutweeklydpm.index, scoutweeklydpm)
ax1.set_ylabel("Avg Weekly DPM")
ax1.set_xlabel("Date")
'''
