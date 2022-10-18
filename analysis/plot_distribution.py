#!/usr/bin/env python
"""Plot a heatmap of all datapoints
*author*: Janosch Walde
"""

# %% import modules
import os
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import numpy as np
from meteohautnah import meteohautnah as mh


def to_nearest(num, decimal):
    return round(num * decimal) / decimal


# %% define paths
data_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/processed/"
plot_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/plots/"
date = "all"  # "2022-05-18"  # yyyy-mm-dd or all
files = os.listdir(data_path)

# %% read in data
df = mh.read_data(data_path, "all", 10)
# extent = [12.2, 12.55, 51.25, 51.43]  # cooler sd effekt, aber verzerrt

# %% select date range
# df = df[df.time.dt.month == 7]  # select June only

# %% gruppiere Punkte in räumlicher Verteilung

# coordinates of midpoint (marketplace in Leipzig)
mp_lon = 12.37534
mp_lat = 51.34038
# insert differenz of coordinates to midpoint
df['lon_diff'] = df.lon - mp_lon
df['lat_diff'] = df.lat - mp_lat
# round differenz to nearest multiple of 4 with 3 digits precision #400
df['group_lon'] = to_nearest(df.lon_diff + mp_lon, 4000)
df['group_lat'] = to_nearest(df.lat_diff + mp_lat, 4000)
# make new df with midpoints of each cell and number of points in it
lons = df.group_lon.unique()
lats = df.group_lat.unique()


# %% Variante 1: Anzahl an nächstem Punkt
df_verteilung = df.groupby(['group_lon', 'group_lat'], as_index=False).agg(dict(air_temperature='count'))
df_verteilung.rename(columns={'air_temperature': 'points', 'group_lon': 'lon', 'group_lat': 'lat'}, inplace=True)

# %% plot temperature on map and add a nice colourbar
plt.rc("font", size=16)
plot_df = df_verteilung  # [::100]  # subsample dataframe if needed
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(projection=request.crs))
extent = [12.25, 12.5, 51.27, 51.42]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 12)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["points"], transform=ccrs.Geodetic(), s=1,
                     cmap="inferno")
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Anzahl an Messpunkten")
ax.set_title("Heatmap MeteoTracker Messpunkte")
plt.tight_layout()
plt.show()
plt.savefig(f"{plot_path}/heatmap_v1.png", dpi=300, transparent=True)
plt.close()


# %% Variante 2: Heatmap

extent = [(12.27, 12.48), (51.27, 51.42)]  # (xmin, xmax, ymin, ymax) andere Karten:[(12.25, 12.5), (51.27, 51.42)]
request = cimgt.OSM()

# plt.rcParams["figure.figsize"] = (8, 8.5)  # all plots with same dimensions
plt.rc("font", size=16)
a = plt.hist2d(df.lon, df.lat, bins=(500, 500), cmap="inferno", range=extent)  # generate Heatmap
plt.title('Heatmap aller Messpunkte')
plt.colorbar(label="Anzahl an Messpunkten")
plt.axis('off')
plt.tight_layout()
plt.show()
plt.savefig(f"{plot_path}/heatmap_v2.png", dpi=300, transparent=True)
plt.close()
