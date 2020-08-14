import logfetch
import spot
import pandas as pd
import matplotlib.pyplot as plt

ID64 = #int
STEAM3 = 'str'

print("Fetching")
fetcher = logfetch.Fetcher('file', ID64, save_directory="dump/mylogs")
logs = fetcher.fetch(do_progress_bar=False, do_file_return=True)

print("Analyzing")
a = spot.Analyze(logs, STEAM3, spot.PLAYEDFULL)
dpm = a.get_timestamped_values(a.DPM)
print(dpm.info())
weeklydpm = a.resample(dpm)


fig, ax1 = plt.subplots()
ax1.plot(weeklydpm.index, weeklydpm)

ax1.set_xlabel("Date")
ax1.set_ylabel("Avg DPM")

plt.show()


