#### IN PROGRESS
#### DOCS COMING SOON

see USAGE_EXAMPLE.py for a usage example  


# logfetch.py
## Basic
Class Fetcher  
Fetcher handles log fetching  
`fetcher = spot.Fetcher(sink, SteamID64, save_directory='??', skip_init=False, earliest=0, latest=999999999999)`  
sink is 'file' to save to file, or 'object' to return only to object and not save files. I highly recommend sinking to files.  
steamID64 if the profile you're getting logs for. See spot.GET_IDs()  
save_directory self explanatory
earliest, latest are ID ranges. IDs higher/lower than these ranges will be excluded. Date ranges coming soon.
skip_init - set this to true if you're going to be using finer controls to assemble your own list.

`fetcher.fetch(do_progress_bar=False, do_file_return=False)`
fetches logs to your sink.  
If do_file_return is true, and your sink is file, it will return a list of json objects. It's basically an alias for from_dir  

`fetcher.from_dir()`  
Returns the opened json objects from save_directory

##Finer controls - these are what are called by the basic functions
`fetcher.get_big_list(steam64ID, limit=10000, offset=0)`
Returns a list of IDs of logs for a profile.  
Limit is limit to return.  
offset is to be used if you need more than 10,000, the max limit.

`fetcher.get_detailed(id)`  
Returns the JSON object for a log id  
This is conservatively ratelimited (30 calls a minute, irrc) due to logs.tf not having a proper backoff protocol or a disclosed query limit.  

## spot.py classes and functions
`GET_IDs(profile)`  
returns a dictionary of steamids. you do not normally access these, you pass the dictionary to functions.  

Class Plotter  
Plotter handles plotting and information sorting / analyzing  
# basic
`plotter = spot.Plotter(logs)`  
logs is the list of json objects you will be analyzing.  
`plotter.plot(stat, bounds=None, method="mean", period="weekly", shade_seasons=False)`  
After you've filtered out your logs with Approver, you can use plot as a highlevel way to quickly plot your graph.  
stat is a stat to filter by. It could be a lambda, accepting log as a param and returning the stat to graph, or probably extractor.DPM  
bounds is a tuple of Datetime, Datetime, or Datetime, None, or None, Datetime, or no tuple at all. Datetime, Datetime -> Start, End.  
method is either mean or sum. It is for graphing the mean (or sum) of your stat over a period.  
period is weekly or monthly.  
shade_seasons will shade in and label seasons for ESEA/RGL
# adv
`df = get_timestamped_values(stat, start=datetime(year=2000, month=1, day=1), end=datetime(year=3000, month=1, day=1))`
returns a pandas DatetimeIndexed Dataframe of your games, with a stat for each game (same rules for stat apply as for plot)  
`plotter.resample(df, method="mean", period='W')`  
resample a dataframe by a method (mean or sum) in a period (w for weekly, m for monthly)  
`data = shade_seasons(self, ax, doText=True)`  
pass a matplotlib axis and it will add shading for TF2 competitive seasons. doText adds labels.  
you can then plot with data.index as x, data as y  


Class Approver  
Approver handles log filtration  
`approver = spot.Approver(IDs, plotter, timecondition, doLog=False, filters={'short', 'dupes', 'non6s', 'medic'}, dont=False)`  
IDs comes from spot.GET_IDs()  
plotter is a Plotter object  
timecondition is '' for all good logs, spot.PLAYEDHALF for logs you played at least half the game, or spot.PLAYEDFULL for logs you played start to finish.  
doLog will do logging.  
Filters is a set of strings for what to filter out   
* short games are less than 600 seconds  
* dupes are double uploads  
* non6s games  
* medic games
each of these funcs can be invoked individually, but i am playing a pug right now and do not wish to document them atm.  
each of the util functions is also available. docs soon :)  
"dont" is a bool. set it to True to not automatically do filters given in your set.  

`approver.Finalize()`  
sets your plotter's logs to the filtered logs  

# Total documentation - stuff you need to know for finer control.