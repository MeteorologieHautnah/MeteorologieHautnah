#!/usr/bin python3

"""Create session IDs and preparing data for analysis
-
*author: Janosch Walde
"""

import os
import pandas as pd
import pytz

# %% define paths
data_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/processed/"
plot_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/plots/"
date = "2022-05-18"  # "2022-05-18"  # yyyy-mm-dd or all
files = os.listdir(data_path)


def read_data(path, dates: str):
    if dates == "all":
        df = pd.concat([pd.read_csv(f"{path}/{file}") for file in files], ignore_index=True)
    else:
        file = [f for f in files if date in f][0]
        df = pd.read_csv(f"{data_path}/{file}")

    # %% filter out values with speed below 10 km/h
    df = df[df.speed > 10]

    # %% Convert time to datetime and to European timezone
    df.loc[:, "time"] = pd.to_datetime(df["time"])  # convert time column to type datetime#
    my_timezone = pytz.timezone('Europe/Berlin')
    df['time'] = df['time'].dt.tz_convert(my_timezone)

    return df


def create_session_id(df):
    session_id = 0
    df.sort_values(["device_id", "time"],
                   ascending=True,
                   inplace=True,)
    dev_id = df.device_id[0]
    t = df.iloc[0, 4]
    df['session_id'] = None
    for i in range(len(df)):
        delta_t = df.iloc[i, 4] - t
        delta_in_s = delta_t.total_seconds()
        if df.iloc[i, 8] == dev_id and delta_in_s <= 300:  # gleiches Gerät und Zeitunterschied kleiner als 5 min
            df.iloc[i, 12] = session_id
            t = df.iloc[i, 4]
        else:
            session_id += 1
            df.iloc[i, 12] = session_id
            t = df.iloc[i, 4]


if __name__ == '__main__':
    df = read_data(data_path, date)
    print(df)
    create_session_id(df)
    print(df[['time', 'device_id', 'session_id']])
