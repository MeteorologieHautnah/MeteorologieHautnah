#!/usr/bin/env python
"""Get some statistics from the dataset for the Übergabeveranstaltung on 02. July 2022

-

*author*: Johannes Röttenbacher
"""

# %% import modules
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

# %% define paths
data_path = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah/Daten/processed"
plot_path = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah/Daten/plots"
date = "all"  # "2022-05-18"  # yyyy-mm-dd or all
files = os.listdir(data_path)
# %% read in data

if date == "all":
    df = pd.concat([pd.read_csv(f"{data_path}/{file}") for file in files])
else:
    file = [f for f in files if date in f][0]
    df = pd.read_csv(f"{data_path}/{file}")

df.loc[:, "time"] = pd.to_datetime(df["time"])  # convert time column to type datetime

# %% filter out values with speed below 10 km/h
df = df[df.speed > 10]

# %% select date range
df = df[df.time.dt.month == 6]  # select June only

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
plt.savefig(f"{plot_path}/juni_temperaturverteilung.png", dpi=100)
plt.close()

# %% get time distribution
df.time.dt.hour.hist(bins=range(0, 25), color="#44AA99", figsize=(10, 6))
plt.xticks(range(25))
plt.xlabel("Uhrzeit (Stunde)")
plt.ylabel("Anzahl Messwerte")
plt.title("Zeitliche Verteilung der Messwerte")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/juni_messzeitverteilung.png", dpi=100)
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
plt.savefig(f"{plot_path}/juni_monatliche_stündliche_mittlere_temperatur.png", dpi=100)
plt.close()

# %% make a boxplot of temperature grouped by hour
df_1.boxplot("air_temperature", by="hour", figsize=(10, 6))
plt.xlabel("Uhrzeit (Stunde)")
plt.ylabel("Temperatur (°C)")
plt.title("Boxplot der Lufttemperatur")
plt.suptitle("")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/juni_stündliche_temperatur_boxplot.png", dpi=100)
plt.close()

# %% filter for group measurement 23. June 16:00 - 22:00
time_min, time_max = pd.Timestamp("2022-06-23 16:00:00 +02"), pd.Timestamp("2022-06-23 23:00:00 +02")
df2 = df[(time_min <= df.time) & (df.time <= time_max)]
# filter one ride from the north
df2 = df2[df2.device_id != "0C:61:CF:A0:AA:B8"]
# filter everything to far east
df2 = df2[df2.lon < 12.37460]

# %% plot map of group measurement
plt.rc("font", size=16)
plot_df = df2  # [::100]  # subsample dataframe if needed
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(8.2, 8.5), subplot_kw=dict(projection=request.crs))
extent = [12.2, 12.40, 51.24, 51.4]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 12)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["air_temperature"], transform=ccrs.Geodetic(),
                     cmap="inferno")
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Temperatur (°C)")
ax.set_title("Gemeinsame Messfahrt 23. Juni")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/juni_gemeinsame_messfahrt_übersicht.png", dpi=300, transparent=True)
plt.close()

# %% plot 3 maps of time evolution
ts1, ts2 = pd.Timestamp("2022-06-23 20:00:00 +02"), pd.Timestamp("2022-06-23 23:00:00 +02")
plt.rc("font", size=16)
# plot_df = df2[df2.time < ts1]
plot_df = df2[(df2.time >= ts1) & (df2.time.max() < ts2)]
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(6.2, 8.4), subplot_kw=dict(projection=request.crs))
extent = [12.27, 12.40, 51.25, 51.4]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 12)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["air_temperature"], transform=ccrs.Geodetic(),
                     cmap="inferno", vmin=20, vmax=35)
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Temperatur (°C)")
# ax.set_title("Gemeinsame Messfahrt vor 20:00")
ax.set_title("Gemeinsame Messfahrt nach 20:00")
plt.tight_layout()
# plt.show()
# plt.savefig(f"{plot_path}/juni_gemeinsame_messfahrt_vor_2000.png", dpi=300, transparent=True)
plt.savefig(f"{plot_path}/juni_gemeinsame_messfahrt_nach_2000.png", dpi=300, transparent=True)
plt.close()
