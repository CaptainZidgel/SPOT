from spot import Fetcher, spot
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

IDs = spot.GET_IDs('')#MAKE THIS YOUR PROFILE OR STEAM64.

print("Fetching")
#If you want to download/update downloaded files:
fetcher = Fetcher(sink='file', IDs=IDs, skip_init=False, save_directory="your_desired_directory")
logs = fetcher.fetch(do_progress_bar=False, do_file_return=True)

#If you only want to work with that you already have downloaded
#fetcher = Fetcher(skip_init=True, save_directory="")
#logs = fetcher.from_dir()

print("Analyzing")
e = spot.Extract(IDs)
plotter = spot.Plotter(logs)
approver = spot.Approver(IDs, plotter, spot.PLAYEDFULL, doLog=True)
approver.Finalize()

#p.plot(e.DPM, method="mean", period="weekly", shade_seasons=False)

seasons = spot.tf2seasons.all_seasons

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4)

dpm = plotter.get_timestamped_values(e.DPM_SCOUT)
scoutweeklydpm = plotter.resample(dpm, period='m')
ax1.plot(scoutweeklydpm.index, scoutweeklydpm) #Resampling requires a value to resample by, so you only need to pass scoutweeklydpm (the returned value) instead of scoutweeklydpm.val. Most other stats you use .val, i think
ax1.set_ylabel("Avg Weekly Scout DPM")

expanding = dpm.expanding().mean()
ax2.plot(expanding.index, expanding.val)
ax2.set_ylabel("Expanding Window Scout DPM")

wl_late = plotter.get_timestamped_values(e.WIN, start=seasons['RGL2']['start'], end=seasons['RGL2']['end']).expanding(5).mean()
ax3.plot(wl_late.index, wl_late.val)

wl = plotter.get_timestamped_values(e.WIN).expanding(50).mean()
ax3.plot(wl.index, wl.val)
ax3.set_ylim(0.2, 0.6)
ax3.set_ylabel("Expanding Window Win%")

ax4.plot(dpm.index, dpm.val) #No sort of resampling or rolling window. Just DPM plotted.
ax4.set_ylabel("DPM per game.")

#I highly recommend you normalize your bounds (limits) where applicable to keep graphs consistent.
#In order to keep things working, the correct order of operations is:
#1. Set y bounds
#2. Set x bounds
#3. Shade seasons, if you wish to do that. (It is essential this comes last if you intend to render labels)
plotter.normalize_ybounds(ax1, ax2) #normalize_ybounds(*axes, margins=5, bot, top) - bot/top are overrides for setting bounds. If non existant, the bounds will be the minimum/maximum values of the included axes, +/- margins.
for ax in (ax1, ax2, ax3, ax4):
    plotter.set_xbounds(ax, None)   #Set the x limits for each axes to start at Jan 1st, 2019 and continue until the end of the data
plotter.shade_seasons(ax2, ax3, doText=True) #Shade seasons for axis 2


fig.show()
