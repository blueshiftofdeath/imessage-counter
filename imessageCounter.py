#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime, sqlite3, csv, os, sys
from datetime import timedelta
from itertools import groupby
from matplotlib.dates import DayLocator, MonthLocator, WeekdayLocator
from matplotlib.dates import AutoDateFormatter, DateFormatter
import argparse

def std_time(stamp):
    basetime_offset = datetime.datetime(2000, 12, 31, 0, 0, 0)
    timezone_offset = 1
    date = basetime_offset + timedelta(timezone_offset, stamp)
    return datetime.date(date.year, date.month, date.day)

def std_list(L):
    L = groupby(L, key = lambda x: x[0])
    counts = []
    for k,g in L:
        counts.append((k, sum(map(lambda x: x[1], g))))
    return counts

def fill_points(target, source):
    target_points = map(lambda row: row[0], target)
    for point in source:
        if point[0] not in target_points:
            target.append((point[0], 0))
    target.sort()

def handleFormat(handles):
    if type(handles) == int:
        return handles
    else:
        return " OR handle_id = ".join(list(map(str, handles)))

def queryMessages(handle, dbName, percent, word=None):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute(
        """
        SELECT date, text, is_from_me
        FROM message
        WHERE handle_id = {}
        """.format(handleFormat(handle))
    )
    result = c.fetchall()

    result = result[int(percent*len(result)):] #only want recent content

    def word_count(text):
        if text is None:
            return 0
        words = text.split()
        if word is not None:
            if " " in word:
                return text.count(word)
            else:
                words = list(filter(lambda x: x.lower() == word, words))
        return len(words)

    result = map(lambda row: (std_time(row[0]), word_count(row[1]), row[2]), result)
    me = std_list([row[:2] for row in result if row[2] == 1])
    other = std_list([row[:2] for row in result if row[2] == 0])

    fill_points(me, other)
    fill_points(other, me)
    return (me, other)

def plot(L1, L2, alt, interval):
    dates1 = [q[0] for q in L1]
    opens1 = [q[1] for q in L1]

    dates2 = [q[0] for q in L2]
    opens2 = [q[1] for q in L2]

    fig, ax = plt.subplots()
    ax.plot_date(dates1, opens1, '-', label='me')
    ax.plot_date(dates2, opens2, '-', label=alt)
    if type(interval) == int:
        # every day
        locator = DayLocator(interval=interval)
        locatorFmt = AutoDateFormatter(locator)
    else:
        # every month
        locator = MonthLocator(range(1, 13), bymonthday=1, interval=1)
        locatorFmt = DateFormatter("%b '%y")
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(locatorFmt)
    ax.xaxis.set_label_text('date')
    ax.yaxis.set_label_text('words')
    plt.legend()
    plt.title('words sent per day by text')
    ax.autoscale_view()
    #ax.xaxis.grid(False, 'major')
    #ax.xaxis.grid(True, 'minor')
    ax.grid(True)

    fig.autofmt_xdate()

    plt.show()

def getHandles(address, dbName):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute(
        """
        SELECT ROWID
        FROM handle
        WHERE id = "{}"
        """.format(address)
    )
    return list(map(lambda x: x[0], c.fetchall()))

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('label', metavar='label', type=str,
                    help='name of person to put in legend')
parser.add_argument('address', metavar='address', type=str,
                    help='phone number or email address used in chat')
parser.add_argument('--word', metavar='word', type=str,
                    help='word to count', required=False)
parser.add_argument('--percent', metavar='percent', type=float,
                    help='how many logs to skip', required=False)
parser.add_argument('--interval', metavar='interval', type=int,
                    help='interval of days to label', required=False)

args = parser.parse_args()

path = os.path.expanduser('~') + '/Library/Messages/chat.db'

if args.percent is not None:
    percent = args.percent
else:
    percent = 0
if args.interval is not None:
    interval = args.interval
else:
    interval = "month"
(me, other) = queryMessages(getHandles(args.address, path), path, percent, word=args.word)
plot(me, other, args.label, interval)
