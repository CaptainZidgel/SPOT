from spot import Fetcher, spot
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
approver = spot.Approver(logs, e, spot.PLAYEDFULL, doLog=True)
logs = approver.logs
logs = spot.LogSeries(logs) #there has to be a better way to do this

fig, (ax1, ax2) = plt.subplots(2)

dpm = logs.timeseries(e.DPM)
ax1.plot(dpm.index, dpm.stats)

dpm_weekly = logs.resample(dpm)
ax2.plot(dpm_weekly.index, dpm_weekly.stats)

fig.show()
