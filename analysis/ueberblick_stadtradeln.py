#!/usr/bin/env python
"""Make some overview plots for Stadtradeln and other participants
-
*author*: Janosch Walde
"""

# %% import modules
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pytz
from meteohautnah import meteohautnah as mh
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import datetime as dt

def to_nearest(num, decimal):
    return round(num * decimal) / decimal


# %% define paths
data_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/processed/"
plot_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/plots/"
group_path = "/home/janosch/Dokumente/MeteorologieHautnah/Daten/stadradeln.csv"
date = "all"  # "2022-05-18"  # yyyy-mm-dd or all
files = os.listdir(data_path)

# %% read in data
df = mh.read_data(data_path, "all", 10)

# %% select date range
df = df[df.time.dt.month == 9]  # select only one month
month = 'September'

# %% prepare Heatmap
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

# %% split groups
stadtradeln_df = pd.read_csv(group_path)
stadtradeln = stadtradeln_df["device_id"]

# Füge Spalte Gruppe hinzu, 1 wenn aus Stadtradeln, 0 wenn nicht
df = df.assign(Gruppe=df.device_id.isin(stadtradeln).astype(int))
# df = df[df.Gruppe == 1]
df_sr = df[df.Gruppe == 1]
df_sonst = df[df.Gruppe == 0]

# %% get time distribution for each group

df_sr.time.dt.hour.hist(bins=range(0, 25), color="#44AA99", figsize=(10, 6))
plt.xticks(range(25))
plt.xlabel("Uhrzeit (Stunde)")
plt.ylabel("Anzahl Messwerte")
plt.title("Zeitliche Verteilung der Messwerte - Stadtradeln")
plt.tight_layout()
#plt.show()
plt.savefig(f"{plot_path}/{month}_messzeitverteilung_sr.png", dpi=100)
plt.close()

df_sonst.time.dt.hour.hist(bins=range(0, 25), color="#44AA99", figsize=(10, 6))
plt.xticks(range(25))
plt.xlabel("Uhrzeit (Stunde)")
plt.ylabel("Anzahl Messwerte")
plt.title("Zeitliche Verteilung der Messwerte - ohne Stadtradeln")
plt.tight_layout()
#plt.show()
plt.savefig(f"{plot_path}/{month}_messzeitverteilung_sonst.png", dpi=100)
plt.close()


# %% einzelne Heatmaps

df_verteilung = df_sonst.groupby(['group_lon', 'group_lat'], as_index=False).agg(dict(air_temperature='count'))
df_verteilung.rename(columns={'air_temperature': 'points', 'group_lon': 'lon', 'group_lat': 'lat'}, inplace=True)

# %% plot temperature on map and add a nice colourbar
plt.rc("font", size=16)
plot_df = df_verteilung  # [::100]  # subsample dataframe if needed
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(projection=request.crs))
extent = [12.28, 12.43, 51.28, 51.39]  # (xmin, xmax, ymin, ymax)[12.25, 12.5, 51.27, 51.42]
ax.set_extent(extent)
ax.add_image(request, 12)
max = df_verteilung.points.max() * 0.3
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["points"], transform=ccrs.Geodetic(), s=1, vmax=max,
                     cmap="inferno")
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Anzahl an Messpunkten")
ax.set_title("Heatmap MeteoTracker Messpunkte")
plt.tight_layout()
#plt.show()
plt.savefig(f"{plot_path}/heatmap_sonst.png", dpi=300, transparent=True)
plt.close()


# %% Übersicht zu Messpunkten pro Tag
# ToDo - noch mit Anzahl der Ausgegebenen Geräte skalieren
# ToDo - Startdatum des Stadtradelns verwenden

df_sr = df_sr.groupby([df_sr.time.dt.date]).agg(dict(air_temperature='count'))
df_sr.rename(columns={'air_temperature': "points"}, inplace=True)
df_sonst = df_sonst.groupby([df_sonst.time.dt.date]).agg(dict(air_temperature='count'))
df_sonst.rename(columns={'air_temperature': "points"}, inplace=True)

plt.plot(df_sr, label="Stadradeln", marker=".")
plt.plot(df_sonst, label="sonstige", marker=".")
plt.xlabel("Datum")
plt.ylabel("Anzahl an Messpunkten")
plt.title("Messpunkte in beiden Gruppen pro Tag")
plt.legend()
plt.tight_layout()
#plt.show()
plt.savefig(f"{plot_path}/distribution_sr_sonst.png", dpi=300, transparent=True)
plt.close()

