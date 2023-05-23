#!/usr/bin/env python
"""Make some overview plots for every month
-
*author*: Johannes Röttenbacher, Janosch Walde
"""

# %% import modules
import meteohautnah.meteohautnah as mh
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def thousands(x, pos):
    """The two arguments are the value and tick position."""
    return f'{x*1e-3:1.0f}'

# %% define paths
base_dir = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah"
data_path = f"{base_dir}/Daten/v1.0/"
plot_path = f"{base_dir}/Daten/plots/Vorbereitungen_abschluss-VA"
date = "all"  # "2022-05-18"  # yyyy-mm-dd or all
files = os.listdir(data_path)

# %% read in data
df = mh.read_data(data_path, date, speedfilter=10)

# %% select date range
df = df[df.time.dt.month == 10]  # select only one month
month = 'Oktober'

# %% calculate some statistics
at_mean, at_min, at_max = df.air_temperature.mean(), df.air_temperature.min(), df.air_temperature.max()

# %% get temperature distribution
plt.rc("font", size=16)
fig, ax = plt.subplots(figsize=(10, 6))
df.air_temperature.hist(bins=40, color="#CC6677", ax=ax)
ax.axvline(at_min, color="#0072B2", label=f"Minimum {at_min:2.1f} °C", linewidth=4)
ax.axvline(at_mean, color="#009E73", label=f"Mittelwert {at_mean:2.1f} °C", linewidth=4)
ax.axvline(at_max, color="#D55E00", label=f"Maximum {at_max:2.1f} °C", linewidth=4)
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
ax.set_xlabel("Temperatur (°C)")
ax.set_ylabel("Anzahl Messwerte (Tausend)")
ax.legend()
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/{month}_temperaturverteilung.png", dpi=300)
plt.close()

# %% get time distribution
plt.rc("font", size=16)
fig, ax = plt.subplots(figsize=(10, 6))
df.time.dt.hour.hist(bins=range(0, 25), color="#44AA99", ax=ax)
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
ax.set_xticks(range(25))
ax.set_xlabel("Lokale Uhrzeit (Stunde)")
ax.set_ylabel("Anzahl Messwerte (Tausend)")
ax.set_title("Zeitliche Verteilung der Messwerte")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/{month}_messzeitverteilung.png", dpi=300)
plt.close()

# %% calculate monthly hourly mean
df_1 = df
df_1["hour"] = df.time.dt.hour
df_grouped = df_1.loc[:, ["air_temperature", "hour"]].groupby("hour").agg([np.mean, np.std]).reset_index()
df_grouped.columns = ["hour", "mean", "std"]  # drop multi index for columns

# %% plot time against temperature
df_grouped.plot.bar(x="hour", y="mean", figsize=(10, 6), color="#CC6677", yerr="std", capsize=4, legend=None)
plt.xlabel("Lokale Uhrzeit (Stunde)")
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
