#!/usr/bin/env python
"""Get some statistics from the dataset for the Abschlussveranstaltung on 19. Ocotber 2022

-

*author*: Johannes Röttenbacher
"""

# %% import modules

import meteohautnah.helpers as h
import meteohautnah.meteohautnah as mh
import os
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt


def thousands(x, pos):
    """The two arguments are the value and tick position."""
    return f'{x*1e-3:1.0f}'

# %% PART 1: General Overview whole dataset
base_dir = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah"
data_path = f"{base_dir}/Daten/v1.0"
plot_path = f"{base_dir}/Daten/plots/Vorbereitungen_abschluss-VA"
date = "all"  # "2022-05-18"  # yyyy-mm-dd or all

# %% read in data
df = mh.read_data(data_path, date, speedfilter=10)
df.time_diff = pd.to_timedelta(df.time_diff)

# %% calculate general dataset statistics
print(f"Number of Measurements between {df.time.iloc[0]:%Y-%m-%d} - {df.time.iloc[-1]:%Y-%m-%d}: {len(df)}")
print(f"Number of Sessions between {df.time.iloc[0]:%Y-%m-%d} - {df.time.iloc[-1]:%Y-%m-%d}: {len(df.session_id.unique())}")

# %% session statistics
df = mh.drop_short_sessions(df)  # drop sessions with only one row left due to speed filter in read in
# calculate statistics for each session
session_stat = df.groupby("session_id").agg(dict(time=[mh.session_change, "first", "last"],
                                                 speed=[np.min, np.max, np.mean],
                                                 air_temperature=[np.min, np.max, np.mean],
                                                 humidity=[np.min, np.max, np.mean],
                                                 pressure=mh.session_change,
                                                 humidex=[mh.session_change, np.min, np.max, np.mean]))
print(f"Longest session duration: ID: {session_stat.iloc[:, 0].argmax()}, {session_stat.iloc[:, 0].max()}")
print(f"Mean session duration: {session_stat.iloc[:, 0].mean()}")

# %% select date range
# df = df[df.time.dt.month == 7]  # select July only

# %% calculate some statistics
at_mean, at_min, at_max = df.air_temperature.mean(), df.air_temperature.min(), df.air_temperature.max()
print(f"Air Temperature\nMin: {at_min}\nMax:{at_max}")

# %% get temperature distribution
plt.rc("font", size=16)
fig, ax = plt.subplots(figsize=(10, 6))
df.air_temperature.hist(bins=40, color="#CC6677", ax=ax)
ax.axvline(at_min, color="#0072B2", label=f"Minimum {at_min:2.1f} °C", linewidth=4)
ax.axvline(at_mean, color="#009E73", label=f"Mittelwert {at_mean:2.1f} °C", linewidth=4)
ax.axvline(at_max, color="#D55E00", label=f"Maximum {at_max:2.1f} °C", linewidth=4)
ax.set_xlabel("Temperatur (°C)")
ax.set_ylabel("Anzahl Messwerte (Tausend)")
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
ax.legend()
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/alle_temperaturverteilung.png", dpi=300)
plt.close()

# %% get time distribution
plt.rc("font", size=16)
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df.time.dt.hour, bins=range(0, 25), color="#44AA99")
for rect in ax.patches:
    height = rect.get_height()
    if height < 20000:
        ax.annotate(f'{int(height)/1000:.1f} K', xy=(rect.get_x()+rect.get_width()/2, height),
                    xytext=(0, 5), textcoords='offset points', ha='center', va='bottom', rotation=90)
ax.set_xticks(range(25))
ax.grid()
ax.set_xlabel("Lokale Uhrzeit (Stunde)")
ax.set_ylabel("Anzahl Messwerte (Tausend)")
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
ax.set_title("Zeitliche Verteilung der Messwerte")
plt.tight_layout()
plt.savefig(f"{plot_path}/alle_messzeitverteilung.png", dpi=300)
plt.show()
plt.close()

# %% plot map of all temperature measurements
plt.rc("font", size=16)
plot_df = df
# map
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(projection=request.crs))
extent = [12.2, 12.55, 51.16, 51.45]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 11)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["air_temperature"], transform=ccrs.Geodetic(),
                     cmap="inferno", alpha=0.5)
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Temperatur (°C)")
ax.set_title(f"Alle Messungen {plot_df.time.iloc[0]:%Y-%m-%d} - {plot_df.time.iloc[-1]:%Y-%m-%d}")
plt.tight_layout()
plt.savefig(f"{plot_path}/alle_temperatur_karte.png", dpi=300, transparent=True)
plt.show()
plt.close()

# %% plot map of all humidity measurements
plt.rc("font", size=16)
plot_df = df
# map
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(projection=request.crs))
extent = [12.2, 12.55, 51.16, 51.45] # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 11)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["humidity"], transform=ccrs.Geodetic(),
                     cmap="YlGn", alpha=0.5)
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Relative Luftfeuchte (%)")
ax.set_title(f"Alle Messungen {plot_df.time.iloc[0]:%Y-%m-%d} - {plot_df.time.iloc[-1]:%Y-%m-%d}")
plt.tight_layout()
plt.savefig(f"{plot_path}/alle_humidity_karte.png", dpi=300, transparent=True)
plt.show()
plt.close()

# %% plot map of all humidex measurements
plt.rc("font", size=16)
plot_df = df
# map
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(projection=request.crs))
extent = [12.2, 12.55, 51.16, 51.45] # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 11)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["humidex"], transform=ccrs.Geodetic(),
                     cmap="hot", alpha=0.5)
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Humidex")
ax.set_title(f"Alle Messungen {plot_df.time.iloc[0]:%Y-%m-%d} - {plot_df.time.iloc[-1]:%Y-%m-%d}")
plt.tight_layout()
plt.savefig(f"{plot_path}/alle_humidex_karte.png", dpi=300, transparent=True)
plt.show()
plt.close()
