#!/usr/bin/env python
"""
| *author:* Johannes Röttenbacher
| *created:* 19.05.2024

Evaluate the data recorded during the StuMeTa workshop 2024

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
import cmcrameri.cm as cm
import seaborn as sns


def thousands(x, pos):
    """The two arguments are the value and tick position."""
    return f'{x*1e-3:1.0f}'

# %% set paths
base_dir = 'C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah'
data_path = f'{base_dir}/Daten/processed'
plot_path = f'{base_dir}/Daten/plots/stumeta2024'
publish_path = './docs/assets/images'
os.makedirs(plot_path, exist_ok=True)
date = '2024-05-09'  # '2022-05-18'  # yyyy-mm-dd or all

# %% setup meta data
group1 = ['04', '05', '06', '07', '19', '20', 'MT2', 'MT5', 'MT9', 'X03']
group2 = ['21', '22', '26', '27', '28', '29', '30', '31', 'X05', 'X06']
iphones = ['06', '19', '20', '26', '27', '28', 'X06']
# ['X06' '27' '20' 'MT2' '31' '07' 'MT5' '30' 'MT9'] actual trackers available in the data set, where is the rest?

# %% read in and filter data
device_ids = pd.read_csv(f'{base_dir}/Daten/device_ids.txt',
                         skipinitialspace=True,
                         )
device_ids = device_ids[device_ids['number'].isin(group1 + group2)]
device_ids['Gruppe'] = np.where(device_ids['number'].isin(group1), 1, 2)
dev_id_col = list()
for n in device_ids['number']:
    if n in iphones:
        dev_id_col.append(device_ids[device_ids['number'] == n]['UUID2'].to_numpy()[0])
    else:
        dev_id_col.append(device_ids[device_ids['number'] == n]['MAC-address'].to_numpy()[0])

device_ids['device_id'] = dev_id_col

# %% read in data
df = mh.read_data(data_path,
                  date=date,
                  speedfilter=0)
df = df.merge(device_ids, on='device_id', how='inner')
df = df.rename({'number': 'Nummer'}, axis=1)
# add column with operating system
df['os'] = np.where(df['Nummer'].isin(iphones), 'iOS', 'Android')

# %% filter by time to remove Oscar's morning and evening session
start_dt = '2024-05-09 16:00'
end_dt = '2024-05-09 18:00'

df = df[df['time'].between(start_dt, end_dt)]

# %% remove first 20 points
# df = mh.remove_points_from_session(df, keep='first', x=20)

# %% timeseries of temperature
plt.rc('font', size=18)
_, ax = plt.subplots(figsize=(18, 9), layout='constrained')
sns.lineplot(data=df, x='time', y='air_temperature', ax=ax,
             hue='Nummer', style='Gruppe', palette=sns.color_palette('flare'))
ax.set(
    title='Zeitreihe der Lufttemperatur',
    xlabel='Zeit (UTC)',
    ylabel='Lufttemperatur (°C)',
)
sns.move_legend(ax, 'upper left', bbox_to_anchor=(1, 1))
ax.grid()
plt.show()
plt.close()

# %% calculate some statistics
at_mean, at_min, at_max = df.air_temperature.mean(), df.air_temperature.min(), df.air_temperature.max()
print(f'Air Temperature\nMin: {at_min}\nMax:{at_max}')

# %% get temperature distribution
plt.rc('font', size=16)
fig, ax = plt.subplots(figsize=(10, 6))
df.air_temperature.hist(bins=40, color='#CC6677', ax=ax)
ax.axvline(at_min, color='#0072B2', label=f'Minimum {at_min:2.1f} °C', linewidth=4)
ax.axvline(at_mean, color='#009E73', label=f'Mittelwert {at_mean:2.1f} °C', linewidth=4)
ax.axvline(at_max, color='#D55E00', label=f'Maximum {at_max:2.1f} °C', linewidth=4)
ax.set_xlabel('Temperatur (°C)')
ax.set_ylabel('Anzahl Messwerte (Tausend)')
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
ax.legend()
plt.tight_layout()
# plt.savefig(f'{plot_path}/alle_temperaturverteilung.png', dpi=300)
plt.show()
plt.close()

# %% plot map of all temperature measurements
plt.rc('font', size=16)
plot_df1 = df[df['Gruppe'] == 1]
plot_df2 = df[df['Gruppe'] == 2]
request = cimgt.OSM()
_, ax = plt.subplots(figsize=(10, 9),
                     subplot_kw=dict(projection=request.crs),
                     layout='constrained')
# extent = [12.2, 12.55, 51.16, 51.45]  # (xmin, xmax, ymin, ymax)
extent = [12.31, 12.44, 51.3, 51.38]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 12)
scatter = ax.scatter(plot_df1['lon'], plot_df1['lat'],
                     c=plot_df1['air_temperature'],
                     transform=ccrs.Geodetic(),
                     cmap=cm.lajolla_r, vmin=17, vmax=23,
                     marker='o')
ax.scatter(plot_df2['lon'], plot_df2['lat'],
           c=plot_df2['air_temperature'],
           transform=ccrs.Geodetic(),
           cmap=cm.lajolla_r, vmin=17, vmax=23,
           marker='x')
cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', pad=0.01,
                    label='Lufttemperatur (°C)')
ax.set_title('Alle MeteoTracker Messpunkte - Lufttemperatur')
plt.savefig(f'{plot_path}/20240509_karte_temperatur.png', dpi=300)
plt.savefig(f'{publish_path}/20240509_karte_temperatur.png', dpi=300)
plt.show()
plt.close()

# %% plot map of all humidity measurements
plt.rc('font', size=16)
plot_df1 = df[df['Gruppe'] == 1]
plot_df2 = df[df['Gruppe'] == 2]
request = cimgt.OSM()
_, ax = plt.subplots(figsize=(10, 9),
                     subplot_kw=dict(projection=request.crs),
                     layout='constrained')
# extent = [12.2, 12.55, 51.16, 51.45]  # (xmin, xmax, ymin, ymax)
extent = [12.31, 12.44, 51.3, 51.38]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 12)
scatter = ax.scatter(plot_df1['lon'], plot_df1['lat'],
                     c=plot_df1['humidity'],
                     transform=ccrs.Geodetic(),
                     cmap=cm.navia, vmin=30, vmax=70,
                     marker='o')
ax.scatter(plot_df2['lon'], plot_df2['lat'],
           c=plot_df2['humidity'],
           transform=ccrs.Geodetic(),
           cmap=cm.navia, vmin=30, vmax=70,
           marker='x')
cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', pad=0.01,
                    label='Relative Feuchtigkeit (%)')
ax.set_title('Alle MeteoTracker Messpunkte - Relative Feuchtigkeit')
plt.savefig(f'{plot_path}/20240509_karte_feuchte.png', dpi=300)
plt.savefig(f'{publish_path}/20240509_karte_feuchte.png', dpi=300)
plt.show()
plt.close()

# %% plot humidity map but only with new Generation of metetracker
plt.rc('font', size=16)
plot_df2 = df[(df['Gruppe'] == 2) & (df['Nummer'] == 'X06')]
request = cimgt.OSM()
_, ax = plt.subplots(figsize=(10, 9),
                     subplot_kw=dict(projection=request.crs),
                     layout='constrained')
# extent = [12.2, 12.55, 51.16, 51.45]  # (xmin, xmax, ymin, ymax)
extent = [12.31, 12.44, 51.3, 51.38]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 12)
ax.scatter(plot_df2['lon'], plot_df2['lat'],
           c=plot_df2['humidity'],
           transform=ccrs.Geodetic(),
           cmap=cm.navia, vmin=30, vmax=70,
           marker='x')
cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', pad=0.01,
                    label='Relative Feuchtigkeit (%)')
ax.set_title('MeteoTracker Messpunkte nur X06 - Relative Feuchtigkeit')
plt.savefig(f'{plot_path}/20240509_karte_feuchte_X06.png', dpi=300)
plt.savefig(f'{publish_path}/20240509_karte_feuchte_x06.png', dpi=300)
plt.show()
plt.close()

# %% plot map of all humidex measurements
plt.rc('font', size=16)
plot_df = df
# map
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(projection=request.crs))
extent = [12.2, 12.55, 51.16, 51.45] # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 11)
scatter = ax.scatter(plot_df['lon'], plot_df['lat'], c=plot_df['humidex'], transform=ccrs.Geodetic(),
                     cmap='hot', alpha=0.5)
cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', label='Humidex')
ax.set_title(f'Alle Messungen {plot_df.time.iloc[0]:%Y-%m-%d} - {plot_df.time.iloc[-1]:%Y-%m-%d}')
plt.tight_layout()
plt.savefig(f'{plot_path}/alle_humidex_karte.png', dpi=300, transparent=True)
plt.show()
plt.close()
# %% read in DWD data
# df_dwd = mh.station_temp(name='Leipzig-Holzhausen',
#                          start_date='2024-05-09',
#                          end_date='2024-05-10')
# df_dwd.reset_index(drop=True, inplace=True)
# # %% add DWD data do dataframe
# df_dwd['device_id'] = 'DWD'
# df_dwd['Gruppe'] = 'DWD'
# df_dwd['Nummer'] = 'DWD'
# df_dwd['time'] = df_dwd.time.dt.tz_localize('Europe/Berlin')
# df = pd.concat([df, df_dwd])

# %% plot timeseries comparison with DWD Station
plt.rc('font', size=18)
_, ax = plt.subplots(figsize=(18, 9))
sns.lineplot(data=df, x='time', y='dewpoint', ax=ax,
             hue='Nummer', style='Gruppe', palette=sns.color_palette('crest'),
             )
sns.lineplot(data=df, x='time', y='air_temperature', ax=ax,
             hue='Nummer', style='Gruppe', legend=False,
             palette=sns.color_palette('flare'))
ax.set(
    title='Zeitreihe der Temperatur',
    xlabel='Zeit (UTC)',
    ylabel='Temperatur (°C)',
)
# make dummy for legend
ax.plot([], color=sns.color_palette('crest')[0], ls='-', label='Taupunkt')
ax.plot([], color=sns.color_palette('flare')[0], ls='-', label='Lufttemperatur')
ax.legend()
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
ax.grid()
plt.savefig(f'{plot_path}/20240509_zeitreihe_temperatur_taupunkt_dwd.png', dpi=300)
plt.savefig(f'{publish_path}/20240509_zeitreihe_temperatur_taupunkt_dwd.png', dpi=300)
plt.show()
plt.close()
