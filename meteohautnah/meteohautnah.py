#!/usr/bin/env python
"""Functions for data processing and analysis for Meteorologie hautnah

*author*: Johannes Röttenbacher, Janosch Walde
"""
import os
import numpy as np
import pandas as pd
import pytz
from wetterdienst.provider.dwd.observation import DwdObservationRequest, DwdObservationDataset, DwdObservationResolution


def read_data(path: str, date: str, speedfilter: float) -> pd.DataFrame:
    """
    Read in data, filter for values > speedfilter (km/h) and convert time from UTC to local time.

    Args:
        path: path where to find csv files
        date: "all" or "yyyy-mm-dd"
        speedfilter: minimum speed of measurement to be kept in dataframe (km/h)

    Returns: pandas Dataframe with columns

    """
    files = os.listdir(path)
    if date == "all":
        df = pd.concat([pd.read_csv(f"{path}/{file}") for file in files], ignore_index=True)
    else:
        file = [f for f in files if date in f][0]
        df = pd.read_csv(f"{path}/{file}")

    # %% filter out values with speed below speedfilter km/h
    df = df[df.speed > speedfilter]

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
        delta_t_min: minimum time difference between old and new session of same device (s)

    Returns: pandas Dataframe with a new column session_id

    """
    session_id = 0
    dev_ids = df.device_id.unique()  # find unique device ids
    df.sort_values(["device_id", "time"], ascending=True, inplace=True)
    df["time_diff"] = df.time.diff()  # add column with time difference
    df = df[df.time_diff != pd.to_timedelta(0)].copy()  # remove duplicated measurements and make sure a copy is returned
    df['session_id'] = None  # add new column for session id
    df_out = pd.DataFrame()
    for dev_id in dev_ids:
        df_tmp = df.loc[df.device_id == dev_id, :].copy()  # select only one device id and return copy
        # get indices with time_diff >= delta_t_min
        idx = np.nonzero(np.asarray(df_tmp["time_diff"] > pd.to_timedelta(delta_t_min, unit="s")))[0]
        idx = np.insert(idx, 0, 0)  # add zero to beginning of indices
        idx = np.append(idx, len(df_tmp))  # add last index
        for i in range(len(idx)-1):
            df_tmp.iloc[slice(idx[i], idx[i+1]), -1] = session_id
            session_id += 1

        df_out = pd.concat([df_out, df_tmp])
    df_out.reset_index(drop=True, inplace=True)

    return df_out


def station_temp(name, start_date, end_date):
    request = DwdObservationRequest(parameter=DwdObservationDataset.TEMPERATURE_AIR,
                                    resolution=DwdObservationResolution.MINUTE_10,
                                    start_date=start_date,
                                    end_date=end_date,
                                    ).filter_by_name(name=name)

    df_res = request.values.all().df.dropna()

    df_Temp = df_res[df_res.parameter == "temperature_air_mean_200"].drop(['dataset', 'parameter', 'quality'], axis=1)
    df_Temp.rename(columns={'value': 'T'}, inplace=True)
    df_dew = df_res[df_res.parameter == "temperature_dew_point_mean_200"].drop(
        ['station_id', 'dataset', 'parameter', 'quality'], axis=1)

    df_dew.rename(columns={'value': 'Td'}, inplace=True)

    df_Temp.set_index(pd.DatetimeIndex(df_Temp['date']), inplace=True)

    df_dew.set_index(pd.DatetimeIndex(df_Temp['date']), inplace=True)

    df_out = df_Temp.merge(df_dew, how='left', left_index=True, right_index=True)
    df_out["time"] = pd.to_datetime(df_Temp.date, format="%Y-%m-%d %H:%M:%S%z").dt.tz_localize(None)
    # df_out["SEC"]=pd.to_timedelta(df_Temp.date).dt.total_seconds()
    df_out.set_index(df_out["time"], inplace=True)
    # df_out.drop(["date"], axis=1)
    # df_out.set_index("time", inplace=True)
    df_out = df_out.drop(["date_x", "date_y"], axis=1)
    df_out["T"] = df_out["T"] - 273.15
    df_out["Td"] = df_out["Td"] - 273.15

    return df_out


def session_change(s):
    """
    Compute change of a variable over a whole session.

    Args:
        s: Series containing a variable for one session

    Returns: Difference between last and first value of given series

    """
    return s.iloc[-1] - s.iloc[0]


def drop_short_sessions(df, x):
    """
    Drop sessions from data frame which only consist of less than x measurements (rows).
    Can be caused by filtering (e.g. speed filter on read in).

    Args:
        df: Data Frame with column session_id
        x: minimum number of points a session needs to have

    Returns: Data Frame with short sessions dropped

    """
    session_stat = df.groupby("session_id").agg(dict(session_id="count"))
    sid_to_drop = list(session_stat[session_stat.session_id < x].index)
    df = df[~df.session_id.isin(sid_to_drop)].copy()

    return df


def remove_last_points_from_session(df: pd.DataFrame, x: float) -> pd.DataFrame:
    """
    Remove last x measurements (rows) from each session in a data frame.

    Args:
        df: DataFrame with session_id column
        x: number of points to remove

    Returns: DataFrame with last x points removed from each session and new index

    """
    session_stat = df.groupby("session_id").agg(dict(session_id='count'))  # number of points per session
    # only select sessions with more points than number of points being removed
    sid_to_drop = list(session_stat[session_stat.session_id > x].index)
    # keep only the last point of each session to extract its index value
    id_to_drop = list(df[df.session_id.isin(sid_to_drop)].drop_duplicates('session_id', keep='last').index)
    # generate a list of index values to drop from the dataset
    ids_to_drop = []
    for i in id_to_drop:
        ids_to_drop += range(i, i - x, -1)
    df.drop(ids_to_drop, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
