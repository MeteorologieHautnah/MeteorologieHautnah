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
    plot_path = f"{base_dir}/Daten/plots/"
    date = "2022-05-03"  # "2022-05-18"  # yyyy-mm-dd or all
    dates = list(pd.date_range("2022-05-01", "2022-10-13").strftime("%Y-%m-%d"))
    # %% read in data, create session id(test for one date)
    # df = mh.read_data(data_path, date, speedfilter=0)
    # print(df)
    # df_new = mh.create_session_id(df)
    # print(df_new[['time', 'device_id', 'session_id']])

    # %% create session id for whole dataset and write to new csv file
    for d in tqdm(dates):
        try:
            df = mh.read_data(data_path, d, speedfilter=0)
        except IndexError:
            print(f"No file found for {d}")
            continue  # Probably no file for this date
        df = mh.create_session_id(df)
        df.to_csv(f"{output_path}/{d}_meteotracker.csv", index=False)
