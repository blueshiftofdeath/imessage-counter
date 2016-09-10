#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime, sqlite3, os
from datetime import timedelta
from itertools import groupby
from matplotlib.dates import DayLocator, MonthLocator, WeekdayLocator
from matplotlib.dates import AutoDateFormatter, DateFormatter
import argparse

#convert timestamp into datetime object
def std_time(stamp):
    basetime_offset = datetime.datetime(2000, 12, 31, 0, 0, 0)
    timezone_offset = 1
    date = basetime_offset + timedelta(timezone_offset, stamp)
    return datetime.date(date.year, date.month, date.day)

#take list of (date, wordCount) tuples and combine tuples with same date
#summing wordCounts
def std_list(L):
    L = groupby(L, key = lambda x: x[0])
    counts = {}
    for k,g in L:
        wordCount = sum(map(lambda x: x[1], g))
        if k in counts:
            counts[k] += wordCount
        else:
            counts[k] = wordCount
    return sorted(list(map(lambda k: (k, counts[k]), counts.keys())))

#target list contains all dates that source contains
def fill_points(target, source):
    target_points = set(map(lambda row: row[0], target))
    for point in source:
        if point[0] not in target_points:
            target.append((point[0], 0))
    target.sort()

def handleFormat(handles):
    if type(handles) == int:
        return handles
    else:
        return " OR handle_id = ".join(list(map(str, handles)))

def zoom(data, start, end):
    if start is not None:
        start = datetime.date(start[0], start[1], start[2])
        data = filter(lambda row: row[0] >= start, data)
    if end is not None:
        end = datetime.date(end[0], end[1], end[2])
        data = filter(lambda row: row[0] <= end, data)
    return sorted(list(data))

def queryMessages(handle, dbName, wordsToCount, split, direction, start, end):
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

    def word_count(text):
        if text is None:
            return 0
        words = text.split()
        if wordsToCount is not None:
            count = 0
            for w in wordsToCount:
                if " " in w:
                    count += text.count(w)
                else:
                    count += len(list(filter(lambda x: x.lower() == w, words)))
            return count
        else:
            return len(words)

    result = zoom(map(lambda row: (std_time(row[0]), word_count(row[1]), row[2]), result), start, end)

    if split:
        me = std_list([row[:2] for row in result if row[2] == 1])
        other = std_list([row[:2] for row in result if row[2] == 0])
        fill_points(me, other)
        fill_points(other, me)
        return (me, other)
    else:
        if direction is not None:
            return std_list([row[:2] for row in result if row[2] == (direction == 'to')])
        else:
            return std_list([row[:2] for row in result])

def addPlot(ax, dataList):
    (label, L) = dataList
    dates = [q[0] for q in L]
    count = [q[1] for q in L]
    ax.plot_date(dates, count, '-', label=label)

def plot(dataLists, interval):
    fig, ax = plt.subplots()
    for dataList in dataLists:
        addPlot(ax, dataList)
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
parser.add_argument('--people', metavar='people', type=str, nargs='*',
                    help='name and address of person to put in legend,\
                          where address is phone number or email address used in chat',
                    required=False)
parser.add_argument('--words', metavar='words', type=str, nargs='*',
                    help='words to count', required=False)
parser.add_argument('--interval', metavar='interval', type=int,
                    help='interval of days to label', required=False)
parser.add_argument('--start', metavar='start', type=int, nargs=3,
                    help='first day to plot', required=False)
parser.add_argument('--end', metavar='end', type=int, nargs=3,
                    help='last day to plot', required=False)
parser.add_argument('-split', action='store_true',
                    help='split count by who sends', required=False)
parser.add_argument('-direction', choices=['to','from'],
                    help='only show given direction', required=False)

args = parser.parse_args()

path = os.path.expanduser('~') + '/Library/Messages/chat.db'

if args.interval is not None:
    interval = args.interval
else:
    interval = "month"

if args.people is not None:
    data = []
    for i in range(len(args.people)/2):
        label = args.people[2*i]
        address = args.people[2*i+1]
        datum = queryMessages(getHandles(address, path),
                              path, args.words, args.split, args.direction,
                              args.start, args.end)
        if args.split:
            (me, other) = datum
            data.append(("me to {}".format(label), me))
            data.append(("{} to me".format(label), other))
        else:
            if args.direction is not None:
                label = "sent {} {}".format(args.direction, label)
            data.append((label, datum))
    plot(data, interval)
