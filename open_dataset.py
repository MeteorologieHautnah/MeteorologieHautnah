#!/usr/bin/env python3
""" Prepare raw data to be published

*author*: janosch Walde
"""

from meteohautnah import meteohautnah as mh

data_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/processed"
data_path_out = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/out"

# %% read in data
df = mh.read_data(data_path, "all", 10)
#df = df[df.time.dt.month == 10]  # select only one month
df = mh.create_session_id(df)


# %% delete all sessions with less than 100 points
session_stat = df.groupby("session_id").agg(dict(session_id='count'))
sid_to_drop = list(session_stat[session_stat.session_id <= 100].index)
df = df[~df.session_id.isin(sid_to_drop)].copy()

# %% get indices for first 50 datapoints for each session and drop them
sid_to_drop = list(session_stat[session_stat.session_id > 100].index)
id_to_drop = list(df[df.session_id.isin(sid_to_drop)].drop_duplicates('session_id', keep='first').index)
ids_to_drop = []
for i in id_to_drop:
    ids_to_drop += range(i, i+50)
df.drop(ids_to_drop, inplace=True)
df.reindex()

# %% get indices for last 50 datapoints for each session and drop them
sid_to_drop = list(session_stat[session_stat.session_id > 100].index)
id_to_drop = list(df[df.session_id.isin(sid_to_drop)].drop_duplicates('session_id', keep='last').index)
ids_to_drop = []
for i in id_to_drop:
    ids_to_drop += range(i, i-50, -1)
df.drop(ids_to_drop, inplace=True)

# %% wrtie data
df.to_csv(data_path_out+"/anonymus_data.csv")

