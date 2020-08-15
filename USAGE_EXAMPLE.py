from spot import Fetcher, spot
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

IDs = spot.GET_IDs('76561198098770013')#MAKE THIS YOUR PROFILE OR STEAM64.

print("Fetching")
#If you want to download/update downloaded files:
#fetcher = Fetcher(sink='file', IDs=IDs, skip_init=False, save_directory="Z:/Projects/SPOT/dump/yourname")
#logs = fetcher.fetch(do_progress_bar=False, do_file_return=True)

#If you only want to work with that you already have downloaded
fetcher = Fetcher(skip_init=True, save_directory="Z:/Projects/SPOT/dump/zidgel")
logs = fetcher.from_dir()

print("Analyzing")
e = spot.Extract(IDs)
plotter = spot.Plotter(logs)
approver = spot.Approver(IDs, plotter, spot.PLAYEDFULL, doLog=True)
approver.Finalize()

#p.plot(e.DPM, method="mean", period="weekly", shade_seasons=False)

fig, (ax1, ax2, ax3) = plt.subplots(3)

dpm = plotter.get_timestamped_values(e.DPM_SCOUT, start=datetime(2019, 1, 1))
scoutweeklydpm = plotter.resample(dpm)
ax1.plot(scoutweeklydpm.index, scoutweeklydpm) #Resampling requires a value to resample by, so you only need to pass scoutweeklydpm (the returned value) instead of scoutweeklydpm.val. Most other stats you use .val, i think
ax1.set_ylabel("Avg Weekly Scout DPM")

expanding = dpm.expanding().mean()
ax2.plot(expanding.index, expanding.val)
ax2.set_ylabel("Expanding Window Scout DPM")

wl = plotter.get_timestamped_values(e.WIN, start=datetime(2019, 1, 1)).expanding(50).mean()
ax3.plot(wl.index, wl.val)
ax3.set_ylim(0.0, 1.0)
ax3.set_ylabel("Expanding Window Win%")

fig.show()
