from datetime import datetime

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
            datetime(2019, 11, 19)),
        2: (datetime(2020, 1, 7),
            datetime(2020, 3, 27)),
        3: (datetime(2020, 5, 19),
            datetime(2020, 8, 6)),
        4: (datetime(2020, 9, 1),
            datetime(2020, 11, 20))
    }

all_seasons = []

for num, ranges in seasons_ESEA.items():
    d = {'start': ranges[0], 'end': ranges[1], 'label': "ESEA"+str(num)}
    all_seasons.append(d)
for num, ranges in seasons_RGL.items():
    d = {'start': ranges[0], 'end': ranges[1], 'label': "RGL"+str(num)}
    all_seasons.append(d)

