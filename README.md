# STATS PLOTTED OVER TIME
#### IN PROGRESS
#### DOCS COMING SOON

see USAGE_EXAMPLE.py for a usage example  

![](example.png?raw=true)

# Todo
Docs

Better plot presets

## Install, Setup
`pip install -r requirements.txt`

`from spot import Fetcher, spot`

## spot classes and functions

`spot.GET_IDs(profile)`  
returns a dictionary of steamids. you do not normally access these, you pass the dictionary to functions.  

##### Class Plotter  
Plotter handles plotting and information sorting / analyzing  
`plotter = spot.Plotter(logs)`  
logs is the list of json objects you will be analyzing. (See: Fetcher)    
`plotter.plot(stat, bounds=None, method="mean", period="weekly", shade_seasons=False)`  
After you've filtered out your logs with Approver, you can use plot as a highlevel way to quickly plot your stats.  
If you know how to use Matplotlib, you can see the Advanced section for functions you can use to get data to make your own graphs.  
stat is a stat to filter by. It could be a lambda, accepting log as a param and returning the stat to graph, or probably extractor.DPM  
bounds is a tuple of Datetime, Datetime, or Datetime, None, or None, Datetime, or no tuple at all. Datetime, Datetime -> Start, End.  
method is either mean or sum. It is for graphing the mean (or sum) of your stat over a period.  
period is weekly or monthly.  
shade_seasons will shade in and label seasons for ESEA/RGL

`df = plotter.get_timestamped_values(stat, start=datetime(year=2000, month=1, day=1), end=datetime(year=3000, month=1, day=1))`
returns a pandas DatetimeIndexed Dataframe of your games, with a stat for each game (same rules for stat apply as for plot)  
`plotter.resample(df, method="mean", period='W')`  
resample a dataframe by a method (mean or sum) in a period (w for weekly, m for monthly)  
`data = plotter.shade_seasons(ax, doText=True)`  
pass a matplotlib axis and it will add shading for TF2 competitive seasons. doText adds labels.  
you can then plot with data.index as x, data as y  
`plotter.set_xbounds(ax, bounds)`  
ax is a matplotlib axis  
bounds is a tuple, but one of the items can be `None`. First value is the left bound, second is the right bound. If a value is `None`, it defaults to the start/end of your data.  
`plotter.normalize_ybounds(*axes, margins=5, bot, top)`  
Set the ylimits for all the axes given. If bot/top are given, use those as bottom/top values.  
Otherwise, use min/max of the total data, +/- margins.  


##### Class Approver  
Approver handles log filtration  
`approver = spot.Approver(IDs, plotter, timecondition, doLog=False, filters={'short', 'dupes', 'non6s', 'medic'}, dont=False)`  
`IDs` comes from spot.GET_IDs()  
`plotter` is a Plotter object  
`timecondition` is '' for all good logs, spot.PLAYEDHALF for logs you played at least half the game, or spot.PLAYEDFULL for logs you played start to finish. (manually invoke: `approver.FilterTimecond(timecondition)`  
`doLog` will do logging. 
`dont` is a bool. set it to True to not automatically do filters given in your set.   
Filters is a set of strings for what to filter out , each of these functions can also be invoked manually (they alter in-place)     
* `short` games are less than 600 seconds  | `approver.FilterShortGames(seconds_logs_must_be_longer_than)`    
* `dupes` are double uploads  | `approver.FilterDupes()`  
* `non6s` games  | `approver.FilterInvalid()`    
* `medic` games  | `approver.FilterMedic()`  
each of these funcs makes use of a util func, you may be interested in invoking these manually as well (they each return a value for one log):  
`approver.GetPlayedTime(log)` Returns seconds player played in a log    
`approver.InvalidFormat(log, p=False)` Returns true for non-6s games, enable p to see its reasoning. 
`approver.DetermineFormatFromOffclasses(log)` Returns true if one person on each team full time offclasses.  
`approver.IsClass(log, classname, percentage)` Returns true if player played class `classname` for `percentage`% of their playtime.


`approver.Custom(lambda)`  
In-place filter for logs that pass lambda.  

`approver.Finalize()`  
sets your plotter's logs to the filtered logs  

## Fetcher
See USAGE_EXAMPLE.py for better docs and practical examples.  
See comments in logfetch.py for more docs.  

### Finer controls - these are what are called by the basic functions
`fetcher.get_big_list(steam64ID, limit=10000, offset=0)`
Returns a list of IDs of logs for a profile.  
Limit is limit to return.  
offset is to be used if you need more than 10,000, the max limit.

`fetcher.get_detailed(id)`  
Returns the JSON object for a log id  
This is conservatively ratelimited (30 calls a minute, if i recall correctly) due to logs.tf not having a proper backoff protocol or a disclosed query limit.  