#!/usr/bin/env python
"""Process the raw json data
Creates an easy-to-read in csv file from the raw json file by cutting off the curl header.
Writes a log file.

usage: python process_raw_json.py [date=yyyymmdd]

*author*: Johannes Röttenbacher
"""
import sys
sys.path.append(".")
from meteohautnah.helpers import read_command_line_args, make_dir
import os
import datetime as dt
import pandas as pd
import logging
from tqdm import tqdm


def preprocess_json(file: str) -> pd.DataFrame:
    """Preprocess raw json file
    Cut of curl message and remove brackets.

    :param file: Full file path
    :return: pandas DataFrame
    """
    with open(file, "r") as f:
        data = f.readlines()[13:][0][1:-1]
        df = pd.read_json(data, lines=True)

    return df


# setup file logger
logdir = "/projekt_agmwend/home_rad/jroettenbacher/meteo_hautnah/logs"
# logdir = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah/Daten/logs"  # for local processing
logfile = f"{logdir}/process_raw_json.log"
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
# loop over all dates
# for date_var in tqdm([d.strftime("%Y%m%d") for d in pd.date_range("2022-05-01", "2022-10-17")]):
logger.info(f"Preprocessing {date_var}")

date_str = dt.datetime.strptime(date_var, "%Y%m%d").strftime("%Y-%m-%d")
indir = f"/projekt_agmwend2/data_raw/meteorologie_hautnah_raw/{date_str}"
outdir = f"/projekt_agmwend/data/meteorologie_hautnah/daily_csv"
# for local processing
# indir = f"C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah/Daten/raw/{date_str}"
# outdir = f"C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah/Daten/processed"

files = os.listdir(indir)  # list all files
if len(files) > 1:
    df = pd.concat([preprocess_json(f"{indir}/{f}") for f in files])  # preprocess files and concatenate them
elif len(files) == 0:
    logger.info(f"No data found for {date_str}")
    sys.exit(1)
else:
    df = preprocess_json(f"{indir}/{files[0]}")

df["lo"] = df["lo"].astype(str)  # convert location column to string
df["lo"] = df["lo"].str.slice(1, -1)  # slice of brackets
df[["lon", "lat"]] = df["lo"].str.split(', ', expand=True)  # split location into lon and lat column
df.drop(["lo"], axis=1, inplace=True)  # drop original location column
header = dict(a="altitude", H="humidity", s="speed", HDX="humidex", time="time", P="pressure", T0="air_temperature",
              td="dewpoint", tag="device_id", L="luminocity", lon="lon", lat="lat")
df = df.rename(columns=header)
# reorder columns
df = df[[h for h in header.values()]]

outfile = f"{outdir}/{date_str}_meteotracker.csv"
df.to_csv(outfile, index=None)  # save data to csv without an index column
logger.info(f"Saved {outfile}")
