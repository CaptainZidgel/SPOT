from datetime import datetime, timedelta
from .tf2seasons import tf2seasons

tf2seasons = tf2seasons()

class PlotHelper:
    """
    Some util functions to help with plotting
    You must pass all your logseries' if you wish to let the class set bounds semi-automatically.
    helper = spot.PlotHelper(series1, series2...)
    """
    def __init__(self, *args):
        if args:
            self._get_minmaxes(*args)
        else:
            self.first = None
            self.last = None
            
    def _get_minmaxes(self, *allseries):
        _all = [log["info"]["date"]
                for series in allseries
                    for log in series.logs
                ] #Flatten
        self.first = datetime.fromtimestamp(min(_all)) - timedelta(days=5)
        self.last = datetime.fromtimestamp(max(_all)) + timedelta(days=5)
    
    def shade_seasons(self, *axes, seasons=tf2seasons.all_seasons, doText=True):
        for ax in axes:
            for lab, s in seasons.items():
                if self.first <= s['start'] <= self.last or self.first <= s['end'] <= self.last:
                    ax.axvspan(s['start'], s['end'], alpha=0.1, color="gray")
                    if doText:
                        ax.text(s['start'], ax.get_ylim()[0], lab, rotation=90, fontsize='small')

    def set_xbounds(self, *axes, bounds=None):
        for ax in axes:
            if bounds == None:
                ax.set_xlim(left=self.first, right=self.last)
            else:
                if bounds[0]:
                    self.first = bounds[0]
                if bounds[1]:
                    self.last = bounds[1]
                ax.set_xlim(left=self.first, right=self.last)

    def normalize_ybounds(self, *axes, margins=5, bot=None, top=None):
        if not bot:
            lowers = [a.get_ylim()[0] for a in axes]
            bot = max(lowers)-margins #this is a little unclear in this case but bot/top are in scope for this entire function because they're kwargs
        if not top:
            uppers = [a.get_ylim()[1] for a in axes]
            top = max(uppers)+margins
        for ax in axes:
            ax.set_ylim(bottom=bot, top=top)
