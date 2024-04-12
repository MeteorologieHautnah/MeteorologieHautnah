#!/usr/bin/env python
"""
| *author:* Johannes Röttenbacher
| *created:* 22.05.2023

Investigate temperature measurements towards their dependency on velocity.
Hypothesis: Higher speeds cause a better air flow through the MeteoTracker resulting in better readings of the temperature sensor.
Strategy: Use measurements during the late afternoon (15 - 16 local time) on a clear sky day with little to no wind and compare them according to the recording speed.
Maybe a more windy/well mixed day would be better for this scenario with overcast sky to avoid local heating effects of the city landscape.
Do both and check if there are differences.

Clear sky days
^^^^^^^^^^^^^^

For the first set of days we used the 18 to 20 July.
A high pressure system over Germany lead to three hot days with no clouds above and hot temperatures in the afternoon.
We select the measurements between 14:00 and 16:00 local time.




"""
# %% import modules
import meteohautnah.meteohautnah as mh
import meteohautnah.helpers as h
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

h.set_cb_friendly_colors()

base_path = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah/Daten"
data_path = f"{base_path}/v1.0"
plot_path = f"{base_path}/plots/tmp"
fig_path = "./analysis/plots_speed_dependency"

# %% read in data and select time
dates = ["2022-05-18", "2022-05-19", "2022-05-20"]  # high pressure, low wind, lots of sun, no cloud
# -> do not show any correlation between speed and normalized air temperature (pearson r: 0.27055)
# try detrending it -> shows even less correlation and a increased spread around 20km/h probably due to more data points there
df = pd.concat([mh.read_data(data_path, date, speedfilter=0) for date in dates])
times = [14, 15]
hour = df.time.dt.hour
selection = ((hour == times[0]) | (hour == times[1]))
df_sel = df.loc[selection]
df_sel = df_sel.set_index(["session_id", "time"])
for var in df_sel:
    try:
        df_sel.loc[:, var] = pd.to_numeric(df_sel[var])
    except ValueError as e:
        print(e)

# %% detrend temperature
df_sel["air_temperature_detrend"] = None
for sid in df_sel.index.get_level_values(0).unique():
    df_to_join = df_sel.xs(sid, level="session_id", drop_level=False)["air_temperature"].diff()
    df_to_join.name = "air_temperature_detrend"
    df_sel.update(df_to_join)

df_sel.loc[:, "air_temperature_detrend"] = pd.to_numeric(df_sel["air_temperature_detrend"])

# %% normalize by the mean of each day
daily_mean = df_sel["air_temperature"].groupby(df_sel.index.get_level_values("time").floor("D")).mean()
daily_std = df_sel["air_temperature"].groupby(df_sel.index.get_level_values("time").floor("D")).std()
var = "air_temperature_norm"
df_sel[var] = None
for t in daily_mean.index:
    df_to_join = (df_sel.xs(f"{t.date()}", level="time")["air_temperature"] - daily_mean[t]) / daily_std[t]
    df_to_join.name = var
    df_sel.update(df_to_join)

df_sel.loc[:, var] = pd.to_numeric(df_sel[var])

# %% plot temperature
var = "air_temperature_detrend"
_, ax = plt.subplots(figsize=h.figsize_wide)
df_sel.plot.scatter("speed", var, ax=ax)
ax.set(xlabel="Speed (km/h)", title=f"Dates: {dates}")
# ax.set_ylabel(ylabel="Air temperature (°C)")
# ax.set_ylabel(ylabel="Normalized air temperature")
ax.set_ylabel(ylabel="Detrended air temperature (°C)")
ax.grid()
figname = f"{fig_path}/{var}-speed_sunny_days.png"
plt.savefig(figname, dpi=300)
plt.show()
plt.close()

# %% compute correlation
df_sel[["speed", "air_temperature"]].reset_index(drop=True).corr()
