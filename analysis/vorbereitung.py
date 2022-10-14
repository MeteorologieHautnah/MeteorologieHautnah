#!/usr/bin python3

"""Create session IDs and preparing data for analysis
-
*author: Janosch Walde
"""

import os
import pandas as pd
import pytz
import meteohautnah.meteohautnah as mh

if __name__ == '__main__':
    # %% define paths
    data_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/processed/"
    plot_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/plots/"
    date = "2022-05-18"  # "2022-05-18"  # yyyy-mm-dd or all
    # %% read in data and create session id
    df = mh.read_data(data_path, date)
    print(df)
    mh.create_session_id(df)
    print(df[['time', 'device_id', 'session_id']])
