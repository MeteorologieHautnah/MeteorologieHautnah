#!/usr/bin/env python
"""
| *author*: Johannes Röttenbacher
| *created*: 26.02.2024

Create overview graphics for a single participant in A4 landscape format.

- Heatmap of tracks
- Distribution of measured temperature
- Times of measurements
- Total kilometers
- Longest session
"""
# %% import modules
import meteohautnah.meteohautnah as mh
import meteohautnah.helpers as h
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

# %% user input
args = h.read_command_line_args()
meteotracker_number = str(args['number']) if 'number' in args else str(28)

# %% set paths
base_path = 'C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah'
data_path = f'{base_path}/Daten/processed'
plot_path = f'{base_path}/Daten/plots/single_participants'

# %% read in and filter data
device_ids = pd.read_csv(f'{base_path}/Daten/device_ids.txt',
                         skipinitialspace=True)
device_id = device_ids['MAC-address'][device_ids["number"] == meteotracker_number]
df = mh.read_data(data_path, 'all', 10)
df = df[df['device_id'] == device_id.iloc[0]]

# %% get years from data
years = df.time.dt.year.unique()

year = years[1]
# %% select data for plotting
plot_df = df[df.time.dt.year == year]

# %% get stats
n_sessions = len(plot_df.session_id.unique())
tmax = plot_df.iloc[plot_df['air_temperature'].argmax()]
tmin = plot_df.iloc[plot_df['air_temperature'].argmin()]
session_stat = (plot_df.groupby('session_id')
                .agg(dict(time=[mh.session_change])))
longest_session = session_stat.max().iloc[0]
average_session_time = session_stat.mean().iloc[0]
total_time = session_stat.sum().iloc[0]
plot_df = (plot_df
           .groupby('session_id')
           .apply(lambda gdf: gdf.assign(distance=mh.add_distance))
           .droplevel(0))

plot_df['cum_distance'] = (plot_df
                           .groupby('session_id')
                           .agg(dict(distance='cumsum')))
complete_distance = plot_df['distance'].sum() / 1000

# make df with locally binned measurements
plot_df["group_lon"] = plot_df.lon.round(3)
plot_df["group_lat"] = plot_df.lat.round(3)
df_verteilung = (df.groupby(['group_lon', 'group_lat'], as_index=False).agg(dict(air_temperature='count')))
df_verteilung.rename(columns={'air_temperature': 'points', 'group_lon': 'lon', 'group_lat': 'lat'}, inplace=True)


# %% plot summary for each year
plt.rc('font', size=12)
fig = plt.figure(figsize=(11.693, 8.268), layout='constrained')
gs = fig.add_gridspec(2, 6)

request = cimgt.OSM()  # get OSM map
loc_stats = plot_df.agg(dict(lat=[min, max], lon=[min, max]))
pad = 0.005
extent = [(loc_stats.lon['min'] - pad, loc_stats.lon['max'] + pad),
          (loc_stats.lat['min'] - pad, loc_stats.lat['max'] + pad)]  # (xmin, xmax, ymin, ymax)
# heatmap
ax1 = fig.add_subplot(gs[0, 0:2], projection=request.crs)
# ax1.set_extent(extent)
ax1.add_image(request, 12)
# scatter = ax1.scatter(plot_df["lon"], plot_df["lat"],
#                       c=plot_df["air_temperature"],
#                       transform=ccrs.Geodetic(),
#                       cmap="inferno")
scatter = ax1.hist2d(plot_df.lon, plot_df.lat, bins=(500, 500), cmin=1, cmap='magma', range=extent, vmax=55)  # generate Heatmap
# cbar = plt.colorbar(scatter, ax=ax1, orientation="horizontal",
#                     label="Temperatur (°C)", pad=-0.05)
ax1.set_title("Alle Messpunkte")
# daily T cycle
ax2 = fig.add_subplot(gs[0, 2:5])

# stats
ax3 = fig.add_subplot(gs[0, -1:])

# T-dist
ax4 = fig.add_subplot(gs[1, 0:3])

# Time-dist
ax5 = fig.add_subplot(gs[1, 3:])

fig.suptitle(f'Meteorology hautnah Zusammenfassung MeteoTracker {meteotracker_number} - {year}')
plt.show()
plt.close()
