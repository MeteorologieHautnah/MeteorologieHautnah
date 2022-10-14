#!/usr/bin/env python
"""Functions for data processing and analysis for Meteorologie hautnah

*author*: Johannes Röttenbacher, Janosch Walde
"""
import os
import pandas as pd
import pytz


def read_data(path: str, date: str) -> pd.DataFrame:
    """
    Read in data, filter for values > 10km/h and convert time from UTC to local time.

    Args:
        path: path where to find csv files
        date: "all" or "yyyy-mm-dd"

    Returns: pandas Dataframe with columns

    """
    files = os.listdir(path)
    if date == "all":
        df = pd.concat([pd.read_csv(f"{path}/{file}") for file in files], ignore_index=True)
    else:
        file = [f for f in files if date in f][0]
        df = pd.read_csv(f"{path}/{file}")

    # %% filter out values with speed below 10 km/h
    df = df[df.speed > 10]

    # %% Convert time to datetime and to European timezone
    df.loc[:, "time"] = pd.to_datetime(df["time"])  # convert time column to type datetime
    my_timezone = pytz.timezone('Europe/Berlin')
    df['time'] = df['time'].dt.tz_convert(my_timezone)

    return df


def create_session_id(df: pd.DataFrame, delta_t_min: float = 300) -> pd.DataFrame:
    """
    Create a session id and add it as a column to the given dataframe.

    Args:
        df: Dataframe as returned by read_data()
        delta_t_min: minimum time difference between old and new session of same device

    Returns: pandas Dataframe with a new column session_id

    """
    session_id = 0
    df.sort_values(["device_id", "time"],
                   ascending=True,
                   inplace=True, )
    dev_id = df.device_id[0]
    t = df.iloc[0, 4]
    df['session_id'] = None
    for i in range(len(df)):
        delta_t = df.iloc[i, 4] - t
        delta_in_s = delta_t.total_seconds()
        # gleiches Gerät und Zeitunterschied kleiner als 5 min
        if df.iloc[i, 8] == dev_id and delta_in_s <= delta_t_min:
            df.iloc[i, 12] = session_id
            t = df.iloc[i, 4]
        else:
            session_id += 1
            df.iloc[i, 12] = session_id
            t = df.iloc[i, 4]

    return df