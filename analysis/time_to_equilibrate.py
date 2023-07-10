#!/usr/bin/env python
"""
| *author:* Johannes Röttenbacher
| *created:* 10.07.2023

Look at different measures to get a good cut off for the start of each session.
Options:
- hard cutoff -> discard first 50 points of each session
- dynamic cut off -> look how long it takes for the gradient to stabilize (move towards zero)
- no cut off but flag according to dynamic cut off
"""
import pandas as pd

# %% import modules
import meteohautnah.helpers as h
import meteohautnah.meteohautnah as mh
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# %% set paths
base_path = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah/Daten"
data_path = f"{base_path}/v1.0"
plot_path = f"{base_path}/plots/tmp"
fig_path = "./analysis/plots_equilibration_time"
h.make_dir(fig_path)

# %% read in data
dates = ["2022-05-17"]
df = mh.read_data(data_path, dates[0], speedfilter=0)
df["time_diff"] = pd.to_timedelta(df["time_diff"])

# %% plot data
df_plot = df.loc[df.session_id == 816]
df_plot = df_plot.loc[df_plot.speed >= 10]
sns.scatterplot(df_plot, x="time", y="air_temperature", hue="speed")
plt.show()
plt.close()

# -> the speed filter does not remove the too warm measurements at the beginning

# %% calculate temperature gradient


# %% plot temperature with gradient and diff
df_plot = df.loc[df.session_id == 816][1:]
df_plot["temperature_gradient"] = np.gradient(df_plot.air_temperature)
df_plot["temperature_diff"] = df.air_temperature.diff()
# sns.scatterplot(df_plot, x="time", y="air_temperature")
sns.lineplot(df_plot, x="time", y="temperature_gradient", label="Gradient")
sns.lineplot(df_plot, x="time", y="temperature_diff", label="Difference")
plt.show()
plt.close()

# -> the gradient and the diff do not seem to make a good criterion

# %% plot temperature with first points removed
for s_id in df.session_id.unique():
# s_id = 816
    for x_remove in [0, 25, 50, 75, 100, 125, 150]:
        df_plot = df.loc[df.session_id == s_id].iloc[x_remove:]
        sns.scatterplot(df_plot, x="time", y="air_temperature", label=x_remove)

    plt.title(s_id)
    plt.savefig(f"{plot_path}/{dates[0]}_{s_id}_temperature_time.png")
    plt.show()
    plt.close()

# -> with at least 50 points removed the sensor seems to be able to reach equilibrium
