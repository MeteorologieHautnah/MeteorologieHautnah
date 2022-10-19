#!/usr/bin python3

"""Create session IDs and preparing data for analysis
-
*author: Janosch Walde
"""

import meteohautnah.meteohautnah as mh
import pandas as pd
from tqdm import tqdm

if __name__ == '__main__':
    # %% define paths
    base_dir = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah"
    # base_dir = "/home/janosch/Dokumente/MeteorologieHautnah"  # Janosch
    data_path = f"{base_dir}/Daten/processed/"
    output_path = f"{base_dir}/Daten/v1.0"
    # date = "2022-05-03"  # "2022-05-18"  # yyyy-mm-dd or all
    dates = list(pd.date_range("2022-05-01", "2022-10-18").strftime("%Y-%m-%d"))  # which dates to save

    # %% read in data, create session id(test for one date)
    # df = mh.read_data(data_path, date, speedfilter=0)
    # print(df)
    # df_new = mh.create_session_id(df)
    # print(df_new[['time', 'device_id', 'session_id']])
    # %% read in data
    df = mh.read_data(data_path, "all", speedfilter=0)

    # %% filter data by location (Leipzig)
    lon_min, lon_max, lat_min, lat_max = 12.2, 12.55, 51.16, 51.45
    location_selection = (df.lon.between(lon_min, lon_max)) & (df.lat.between(lat_min, lat_max))
    df = df[location_selection].copy()

    # %% create session id for whole dataset and write to new csv file
    df = mh.create_session_id(df)
    # drop sessions which only consist of one row/entry
    df = mh.drop_short_sessions(df)
    # create new session ids after dropping sessions
    df = mh.create_session_id(df)
    date_str = df.time.dt.strftime("%Y-%m-%d")  # create series of dates for writing to csv files

    for d in tqdm(dates):
        df_out = df[d == date_str]
        df_out.to_csv(f"{output_path}/{d}_meteotracker.csv", index=False)



