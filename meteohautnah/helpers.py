#!/usr/bin/env python
"""Helper functions

*author*: Johannes Röttenbacher
"""
import sys
import os
import matplotlib
import matplotlib.pyplot as plt
import datetime


def read_command_line_args():
    """
    Read out command line arguments and save them to a dictionary. Expects arguments in the form key=value.

    Returns: dictionary with command line arguments as dict[key] = value

    """
    args = dict()
    for arg in sys.argv[1:]:
        if arg.count('=') == 1:
            key, value = arg.split('=')
            args[key] = value

    return args


def make_dir(folder: str) -> None:
    """
    Creates folder if it doesn't exist already.

    Args:
        folder: folder name or full path

    Returns: nothing, but creates a new folder if possible

    """
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass


# from pyLARDA.Transformations
def set_xticks_and_xlabels(ax: plt.axis, time_extend: datetime.timedelta) -> plt.axis:
    """This function sets the ticks and labels of the x-axis (only when the x-axis is time in UTC).

    Options:
        -   time_extend > 7 days:               major ticks every 2 day,  minor ticks every 12 hours
        -   7 days > time_extend > 2 days:      major ticks every day, minor ticks every  6 hours
        -   2 days > time_extend > 1 days:      major ticks every 12 hours, minor ticks every  3 hours
        -   1 days > time_extend > 12 hours:    major ticks every 2 hours, minor ticks every  30 minutes
        -   12hours > time_extend > 6 hours:    major ticks every 1 hours, minor ticks every  30 minutes
        -   6 hours > time_extend > 2 hour:     major ticks every hour, minor ticks every  15 minutes
        -   2 hours > time_extend > 15 min:     major ticks every 15 minutes, minor ticks every 5 minutes
        -   15 min > time_extend > 5 min:       major ticks every 15 minutes, minor ticks every 5 minutes
        -   else:                               major ticks every minute, minor ticks every 10 seconds

    Args:
        ax: axis in which the x-ticks and labels have to be set
        time_extend: time difference of t_end - t_start (format datetime.timedelta)

    Returns:
        ax - axis with new ticks and labels
    """

    if time_extend > datetime.timedelta(days=30):
        pass
    elif datetime.timedelta(days=30) > time_extend >= datetime.timedelta(days=7):
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(bymonthday=range(1, 32, 2)))
        ax.xaxis.set_minor_locator(matplotlib.dates.HourLocator(byhour=range(0, 24, 12)))
    elif datetime.timedelta(days=7) > time_extend >= datetime.timedelta(days=2):
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=[0]))
        ax.xaxis.set_minor_locator(matplotlib.dates.HourLocator(byhour=range(0, 24, 6)))
    elif datetime.timedelta(days=2) > time_extend >= datetime.timedelta(hours=25):
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %d\n%H:%M'))
        ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=range(0, 24, 12)))
        ax.xaxis.set_minor_locator(matplotlib.dates.HourLocator(byhour=range(0, 24, 3)))
    elif datetime.timedelta(hours=25) > time_extend >= datetime.timedelta(hours=12):
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=range(0, 24, 2)))
        ax.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator(byminute=range(0, 60, 30)))
    elif datetime.timedelta(hours=12) > time_extend >= datetime.timedelta(hours=6):
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(matplotlib.dates.HourLocator())
        ax.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator(byminute=range(0, 60, 30)))
    elif datetime.timedelta(hours=6) > time_extend >= datetime.timedelta(hours=2):
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(interval=1))
        ax.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator(byminute=range(0, 60, 15)))
    elif datetime.timedelta(hours=2) > time_extend >= datetime.timedelta(minutes=15):
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(byminute=range(0, 60, 15)))
        ax.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator(byminute=range(0, 60, 5)))
    elif datetime.timedelta(minutes=15) > time_extend >= datetime.timedelta(minutes=5):
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(byminute=range(0, 60, 15)))
        ax.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator(byminute=range(0, 60, 5)))
    else:
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(byminute=range(0, 60, 1)))
        ax.xaxis.set_minor_locator(matplotlib.dates.SecondLocator(interval=10))

    return ax


def set_cb_friendly_colors():
    """Set new colorblind friendly color cycle.

    Returns: Modifies the standard pyplot color cycle

    """
    cb_color_cycle = ["#88CCEE", "#CC6677", "#DDCC77", "#117733", "#332288", "#AA4499", "#44AA99", "#999933", "#882255",
                      "#661100", "#6699CC", "#888888"]
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=cb_color_cycle)

