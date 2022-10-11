#!/usr/bin/env python
"""Make some overview plots for every month
-
*author*: Johannes Röttenbacher, Janosch Walde
"""

# %% import modules
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pytz

# %% define paths
data_path = "/home/janosch/Dokumente/Meteotracker/Daten/processed/"
plot_path = "/home/janosch/Dokumente/Meteotracker/Daten/plots/"
date = "all"  # "2022-05-18"  # yyyy-mm-dd or all
files = os.listdir(data_path)

# %% read in data
if date == "all":
    df = pd.concat([pd.read_csv(f"{data_path}/{file}") for file in files])
else:
    file = [f for f in files if date in f][0]
    df = pd.read_csv(f"{data_path}/{file}")

df.loc[:, "time"] = pd.to_datetime(df["time"])  # convert time column to type datetime#
my_timezone = pytz.timezone('Europe/Berlin')
df['time'] = df['time'].dt.tz_convert(my_timezone)

# %% filter out values with speed below 10 km/h
df = df[df.speed > 10]

# %% select date range
df = df[df.time.dt.month == 8]  # select only one month
month = 'August'

# %% calculate some statistics
at_mean, at_min, at_max = df.air_temperature.mean(), df.air_temperature.min(), df.air_temperature.max()

# %% get temperature distribution
df.air_temperature.hist(bins=40, color="#CC6677", figsize=(10, 6))
plt.axvline(at_min, color="#0072B2", label=f"Minimum {at_min:2.1f} °C", linewidth=4)
plt.axvline(at_mean, color="#009E73", label=f"Mittelwert {at_mean:2.1f} °C", linewidth=4)
plt.axvline(at_max, color="#D55E00", label=f"Maximum {at_max:2.1f} °C", linewidth=4)
plt.xlabel("Temperatur (°C)")
plt.ylabel("Anzahl Messwerte")
plt.legend()
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/{month}_temperaturverteilung.png", dpi=100)
plt.close()

# %% get time distribution
df.time.dt.hour.hist(bins=range(0, 25), color="#44AA99", figsize=(10, 6))
plt.xticks(range(25))
plt.xlabel("Uhrzeit (Stunde)")
plt.ylabel("Anzahl Messwerte")
plt.title("Zeitliche Verteilung der Messwerte")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/{month}_messzeitverteilung.png", dpi=100)
plt.close()

# %% calculate monthly hourly mean
df_1 = df
df_1["hour"] = df.time.dt.hour
df_grouped = df_1.loc[:, ["air_temperature", "hour"]].groupby("hour").agg([np.mean, np.std]).reset_index()
df_grouped.columns = ["hour", "mean", "std"]  # drop multi index for columns

# %% plot time against temperature
df_grouped.plot.bar(x="hour", y="mean", figsize=(10, 6), color="#CC6677", yerr="std", capsize=4, legend=None)
plt.xlabel("Uhrzeit (Stunde)")
plt.ylabel("Temperatur (°C)")
plt.title("Monatliches Mittel der stündlichen Mittel mit Standardabweichung")
plt.grid()
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/{month}_monatliche_stündliche_mittlere_temperatur.png", dpi=100)
plt.close()

# %% make a boxplot of temperature grouped by hour
df_1.boxplot("air_temperature", by="hour", figsize=(10, 6))
plt.xlabel("Uhrzeit (Stunde)")
plt.ylabel("Temperatur (°C)")
plt.title("Boxplot der Lufttemperatur")
plt.suptitle("")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/{month}_stündliche_temperatur_boxplot.png", dpi=100)
plt.close()
