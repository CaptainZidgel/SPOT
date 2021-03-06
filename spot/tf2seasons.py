from datetime import datetime, timedelta
"""
ESEA information was taken from the standings page for each season,
which provides a time range of when the season "was"
RGL information was taken from Trad 6s past events page for beginnings, and league table
for endings. I set the ending to be the latest finals date I could find for the top divs.
Beginnings do not include preseason.
"""
class tf2seasons:
    def __init__(self, include_late=True):
        self.all_seasons = {}

        seasons_ESEA = {
            3: (datetime(2009, 5, 4), datetime(2009, 8, 2)),
            4: (datetime(2009, 8, 9), datetime(2009, 11, 15)),
            5: (datetime(2009, 11, 30), datetime(2010, 3, 6)),
            6: (datetime(2010, 4, 12), datetime(2010, 7, 13)),
            7: (datetime(2010, 7, 23), datetime(2010, 11, 30)),
            8: (datetime(2011, 1, 6), datetime(2011, 4, 14)),
            9: (datetime(2011, 6, 13), datetime(2011, 9, 25)),
            10: (datetime(2011, 10, 18), datetime(2012, 2, 12)),
            11: (datetime(2012, 3, 26), datetime(2012, 7, 13)),
            12: (datetime(2012, 7, 30), datetime(2012, 11, 18)),
            13: (datetime(2012, 11, 28), datetime(2013, 4, 21)),
            14: (datetime(2013, 5, 13), datetime(2013, 8, 25)),
            15: (datetime(2013, 9, 30), datetime(2014, 1, 15)),
            16: (datetime(2014, 3, 3), datetime(2014, 6, 22)),
            17: (datetime(2014, 7, 14), datetime(2014, 10, 26)),
            18: (datetime(2015, 1, 5), datetime(2015, 4, 19)),
            19: (datetime(2015, 4, 29), datetime(2015, 7, 19)),
            20: (datetime(2015, 9, 2), datetime(2015, 12, 16)),
            21: (datetime(2016, 1, 20), datetime(2016, 4, 26)),
            22: (datetime(2016, 5, 24), datetime(2016, 8, 28)),
            23: (datetime(2016, 9, 12), datetime(2016, 12, 18)),
            24: (datetime(2017, 1, 26), datetime(2017, 3, 27)),
            25: (datetime(2017, 6, 1), datetime(2017, 8, 6)),
            26: (datetime(2017, 9, 18), datetime(2017, 12, 4)),
            27: (datetime(2018, 1, 15), datetime(2018, 3, 26)),
            28: (datetime(2018, 5, 14), datetime(2018, 7, 22)),
            29: (datetime(2018, 9, 10), datetime(2018, 11, 18)),
            30: (datetime(2019, 1, 7), datetime(2019, 3, 17)),
            31: (datetime(2019, 4, 22), datetime(2019, 6, 30))
            }

        seasons_RGL = {
                1: (datetime(2019, 6, 24),
                    datetime(2019, 11, 20)),
                2: (datetime(2020, 1, 7),
                    datetime(2020, 4, 2)),
                3: (datetime(2020, 5, 19),
                    datetime(2020, 8, 15)),
                4: (datetime(2020, 9, 14),
                    datetime(2020, 12, 20))
            }

        for num, ranges in seasons_ESEA.items():
            label = "ESEA"+str(num)
            self.all_seasons[label] = {'start': ranges[0], 'end': ranges[1] }
        for num, ranges in seasons_RGL.items():
            label = "RGL"+str(num)
            self.all_seasons[label] = {'start': ranges[0], 'end': ranges[1] }

        if include_late:
            for ranges in self.all_seasons.values():
                ranges['end'] = ranges['end'] + timedelta(hours=25)
        '''
        Datetimes with no hour/minute specified default to midnight, morning of date. (local time)
        TF2 games are played very late, and perhaps after midnight EST in the case of long finals.
        include_late will add 25 hours to each end date. Otherwise, only add 23 hours.
        I don't know why you would want to turn this off, but the option is there.
        '''
