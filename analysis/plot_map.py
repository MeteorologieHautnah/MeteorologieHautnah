#!/usr/bin/env python
"""Plot a map of the given input

*author*: Johannes Röttenbacher
"""

# %% import modules
import os
import pandas as pd
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
df = df[df.time.dt.month == 1]  # select June only

# %% select device_id
device_id = "2B5E2251-11FF-A25E-0CFA-84F8DEAE59F2"
df = df[df.device_id == device_id]

df = df[df.air_temperature < 0]

# %% plot temperature on map and add a nice colorbar
plt.rc("font", size=16)
plot_df = df  # [::100]  # subsample dataframe if needed
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(projection=request.crs))
extent = [12.2, 12.55, 51.16, 51.45]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 12)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["air_temperature"], transform=ccrs.Geodetic(),
                     cmap="inferno")
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Temperatur (°C)")
ax.set_title("Alle MeteoTracker Messpunkte - Juli 2022")
plt.tight_layout()
# plt.savefig(f"{plot_path}/alle_messungen_juli.png", dpi=300, transparent=True)
plt.show()
plt.close()
