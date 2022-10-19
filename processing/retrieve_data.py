#!/usr/bin/env python
"""Retrieve data from ioTopon server

Writes json file(s) to a date folder which it creates and a log file to a log folder.

usage: python retrieve_data.py [date=yyyymmdd]

*author*: Johannes Röttenbacher
"""
import sys
sys.path.append(".")
from meteohautnah.helpers import read_command_line_args, make_dir
import os
import datetime as dt
import subprocess
import re
import logging
import pandas as pd
from tqdm import tqdm

# setup file logger
logdir = "/projekt_agmwend/home_rad/jroettenbacher/meteo_hautnah/logs"
logfile = f"{logdir}/retrieve_data.log"
logger = logging.getLogger(__name__)
handler = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s', datefmt="%c")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# standard options
yesterday = dt.datetime.now() - dt.timedelta(days=1)
date_var = yesterday.strftime("%Y%m%d")
# read in command line args to overwrite standard options
args = read_command_line_args()
date_var = args["date"] if "date" in args else date_var
# get MeteoTracker Token from environment variables
mttoken = os.environ.get("mttoken")
# loop over all dates
# for date_var in tqdm([d.strftime("%Y%m%d") for d in pd.date_range("2022-05-01", "2022-10-17")]):
logger.info(f"-------------------------------------------------------------------------------------------------------\n"
            f"Working on {date_var}\n\n")

date_str = dt.datetime.strptime(date_var, "%Y%m%d").strftime("%Y-%m-%d")
outdir = f"/projekt_agmwend2/data_raw/meteorologie_hautnah_raw/{date_str}"
# create output directory
make_dir(outdir)

number_of_points = 1  # initialize while loop variable
n = 0  # initialize count
while number_of_points > 0:
    outfile = f"{outdir}/{date_str}_meteotracker_{n:02}.json"
    url = f"https://app.meteotracker.com/api/uni-leipzig/{date_str}T00:00:00Z/{n}"
    with open(outfile, "w") as f:
        with open(logfile, "a") as log:
            subprocess.run(["curl", "-i", url, "-X", "GET", "-H", f"Authorization: Bearer {mttoken}"], stdout=f, stderr=log)

    # read first line of json file to get number of points retrieved with curl
    with open(outfile, "r") as f:
        line = f.readline()
        try:
            number_of_points = int(re.search(r"(\d+) (points)", line).group(1))
        except AttributeError:
            logger.info("Did not download any points! Check scripts!")
            os.remove(outfile)  # remove empty file
            sys.exit(1)
    n += 1

os.remove(outfile)  # remove last outfile
logger.info(f"Done with downloading data for {date_var}\n")
