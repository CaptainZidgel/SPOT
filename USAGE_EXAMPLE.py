from spot import Fetcher, PlotHelper, spot
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

Zid = spot.GET_IDs('76561198098770013')#MAKE THIS YOUR PROFILE OR STEAM64.

print("Fetching")
#If you only want to work with that you already have downloaded
fetcher = Fetcher(skip_init=True, save_directory = os.path.join("Z:/log_dumps", str(Zid['64'])))
logs = fetcher.from_dir()

print("Analyzing")
e = spot.Extract(Zid)
logs_com = spot.LogSeries(logs)
logs_med = spot.LogSeries(logs) #This is actually kind of cringe but a RARE use case, especially considering I'm the only user :D
logs_com.StdFilter(e, spot.PLAYEDFULL, logging=True, remove={"short", "dupes", "non6s", "medic"})
logs_med.StdFilter(e, spot.PLAYEDFULL, logging=True, remove={"short", "dupes", "non6s", "combat"})

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4)

dpm = logs_com.timeseries(e.DPM)
ax1.plot(dpm.index, dpm.stats)

dpm_weekly = logs_com.resample(dpm)
ax2.plot(dpm_weekly.index, dpm_weekly.stats)

dpm_ew = dpm.expanding(25).mean()
ax3.plot(dpm_ew.index, dpm_ew.stats)

hpm = logs_med.timeseries(e.MED_HPM)
hpm_ew = hpm.expanding(25).mean()
ax4.plot(hpm_ew.index, hpm_ew.stats)

'''
wins = logs.timeseries(e.WIN)
wins_sum = wins.rolling(100).sum() #This is a cringe graph that tells you information you can get in clearer ways, but you could make it if you wanted to.
ax4.plot(wins_sum.index, wins_sum.stats)
'''

p = PlotHelper(logs_com)
p.shade_seasons(ax1, ax2)
p.set_xbounds(ax1, ax2, ax3)
p.normalize_ybounds(ax1, ax2, ax3, bot=100, top=370)

fig.show()
