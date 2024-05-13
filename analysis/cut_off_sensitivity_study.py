#!/usr/bin/env python
"""
| *author*: Johannes Röttenbacher
| *created*: 23.05.2023

Investigate the effect of cutting of X number of points from the start and end of each session to anonymize the data.
"""

# %% import modules
import meteohautnah.meteohautnah as mh
import meteohautnah.helpers as h
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %% set paths
base_path = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah"
data_path = f"{base_path}/Daten/v1.0/"
plot_path = f"{base_path}/Daten/plots/cut_off_sensitivity_study"

# %% read in data
df = mh.read_data(data_path, "all", 0)

# %% calculate temperature gradiant between each measurement
df["temp_diff"] = df.air_temperature.diff()
df["temp_diff"].mask(df["count"] == 0, inplace=True)
df["gradient"] = np.gradient(df.air_temperature)
df["count"] = df.groupby("session_id").cumcount()

# apply speed filter
df1 = df[df.speed >= 10].copy()
df1["count"] = df1.groupby("session_id").cumcount()
df1.reset_index(inplace=True, drop=True)
# remove x points from the end of each session
x = 20
df2 = mh.remove_last_points_from_session(df1, x)

# %% plot mean gradient for each session
sns.relplot(df2, x="count", y="temp_diff", hue="session_id")
# plt.title(f"Unfiltered data")
# plt.title(f"Speed filtered (10 km/h)")
plt.title(f"Speed filtered (10 km/h) + removed last {x} points")
plt.tight_layout()
plt.show()
plt.close()
