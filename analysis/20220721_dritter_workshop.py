#!/usr/bin/env python
"""Get some statistics from the dataset for the Übergabeveranstaltung on 02. July 2022

-

*author*: Johannes Röttenbacher
"""

# %% import modules

import meteohautnah.helpers as h
import os
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from wetterdienst.provider.dwd.observation import DwdObservationRequest, DwdObservationDataset, DwdObservationPeriod, DwdObservationResolution

# %% define functions


def station_temp(name, start_date, end_date):
    request = DwdObservationRequest(parameter=DwdObservationDataset.TEMPERATURE_AIR,
                                    resolution=DwdObservationResolution.MINUTE_10,
                                    start_date=start_date,
                                    end_date=end_date,
                                    ).filter_by_name(name=name)

    df_res = request.values.all().df.dropna()

    df_Temp = df_res[df_res.parameter == "temperature_air_mean_200"].drop(['dataset', 'parameter', 'quality'], axis=1)
    df_Temp.rename(columns={'value': 'T'}, inplace=True)
    df_dew = df_res[df_res.parameter == "temperature_dew_point_mean_200"].drop(
        ['station_id', 'dataset', 'parameter', 'quality'], axis=1)

    df_dew.rename(columns={'value': 'Td'}, inplace=True)

    df_Temp.set_index(pd.DatetimeIndex(df_Temp['date']), inplace=True)

    df_dew.set_index(pd.DatetimeIndex(df_Temp['date']), inplace=True)

    df_out = df_Temp.merge(df_dew, how='left', left_index=True, right_index=True)
    df_out["time"] = pd.to_datetime(df_Temp.date, format="%Y-%m-%d %H:%M:%S%z").dt.tz_localize(None)
    # df_out["SEC"]=pd.to_timedelta(df_Temp.date).dt.total_seconds()
    df_out.set_index(df_out["time"], inplace=True)
    # df_out.drop(["date"], axis=1)
    # df_out.set_index("time", inplace=True)
    df_out = df_out.drop(["date_x", "date_y"], axis=1)
    df_out["T"] = df_out["T"] - 273.15
    df_out["Td"] = df_out["Td"] - 273.15

    return df_out

# %% PART 1: Sebastians Rides define paths
data_path = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah/Daten/csvs"
# data from Sebastian only (JR 21.07.22)
plot_path = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah/Daten/plots"
date = "all"  # "2022-05-18"  # yyyy-mm-dd or all
files = os.listdir(data_path)

# %% read in data
file1 = files[0]
file2 = files[1]
df1 = pd.read_csv(f"{data_path}/{file1}")
df2 = pd.read_csv(f"{data_path}/{file2}")

df1.loc[:, "time"] = pd.to_datetime(df1["time"])  # convert time column to type datetime
df2.loc[:, "time"] = pd.to_datetime(df2["time"])  # convert time column to type datetime

# dwd data
dwd_df = station_temp("Holzhausen", pd.to_datetime("2022-07-18 00:00"), pd.to_datetime("2022-07-19 00:00"))
dwd_df.set_index(pd.to_datetime(dwd_df.index, utc=True), inplace=True)


# %% interpolate DWD data to MeteoTracker data
df1 = df1.set_index(df1.time)
df1 = df1.merge(dwd_df["T"], how="outer", sort=True, left_index=True, right_index=True)
df1["T"] = df1["T"].interpolate(method="time", inplace=False, axis=0)

df2 = df2.set_index(df2.time)
df2 = df2.merge(dwd_df["T"], how="outer", sort=True, left_index=True, right_index=True)
df2["T"] = df2["T"].interpolate(method="time", inplace=False, axis=0)

# %% drop nan values
df1 = df1.dropna()
df2 = df2.dropna()

# %% plot map of measurements
plt.rc("font", size=16)
plot_df = df1  # [::10]  # subsample dataframe if needed
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(6.8, 9), subplot_kw=dict(projection=request.crs))
extent = [12.35, 12.43, 51.31, 51.4]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 12)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["Temp[°C]"], transform=ccrs.Geodetic(),
                     cmap="inferno", vmax=33.5, vmin=28.5)
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Temperatur (°C)")
ax.set_title(f"Messfahrt 18. Juli 2022 - {plot_df.time.iloc[0]:%H:%M} - {plot_df.time.iloc[-1]:%H:%M} UTC")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/20220718_F46077A2930C_1_karte.png", dpi=300, transparent=True)
plt.close()

plt.rc("font", size=16)
plot_df = df2  # [::10]  # subsample dataframe if needed
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(6.8, 9), subplot_kw=dict(projection=request.crs))
extent = [12.35, 12.43, 51.31, 51.4]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 12)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["Temp[°C]"], transform=ccrs.Geodetic(),
                     cmap="inferno", vmax=33.5, vmin=28.5)
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Temperatur (°C)")
ax.set_title(f"Messfahrt 18. Juli 2022 - {plot_df.time.iloc[0]:%H:%M} - {plot_df.time.iloc[-1]:%H:%M} UTC")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/20220718_F46077A2930C_2_karte.png", dpi=300, transparent=True)
plt.close()

# %% plot time series over latitude of both runs
plt.rc("font", size=16)
plot_df1, plot_df2 = df1.iloc[50:-50], df2.iloc[50:-50]
h.set_cb_friendly_colors()
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(plot_df1.lat, plot_df1["Temp[°C]"].values, label="Nachmittag", linewidth=3)
ax.plot(plot_df2.lat, plot_df2["Temp[°C]"].values, label="Abend", linewidth=3)
# h.set_xticks_and_xlabels(ax, (df2.time.iloc[-1] - df1.time.iloc[0]))
ax.set_xlabel("Latitude (°)")
ax.set_ylabel("Lufttemperatur (°C)")
ax.set_title("Zwei Messfahrten entlang einer Nord-Süd Achse \ndurch die Leipziger Innenstadt vom 18. Juli 2022")
ax.grid()
ax.legend()
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/20220718_F46077A2930C_temp-lat_zeitreihe.png", dpi=200)
plt.close()

# %% plot time series of both runs
plot_df1, plot_df2 = df1.iloc[50:-50], df2.iloc[50:-50]
h.set_cb_friendly_colors()
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(plot_df1.time, plot_df1["Temp[°C]"].values, label="Mittag", linewidth=3)
ax.plot(plot_df2.time, plot_df2["Temp[°C]"].values, label="Abend", linewidth=3)
# h.set_xticks_and_xlabels(ax, (df2.time.iloc[-1] - df1.time.iloc[0]))
ax.set_xlabel("Zeit (UTC)")
ax.set_ylabel("Lufttemperatur (°C)")
ax.set_title("")
ax.grid()
ax.legend()
plt.tight_layout()
plt.show()
# plt.savefig(f"{plot_path}/juni_monatliche_stündliche_mittlere_temperatur.png", dpi=100)
plt.close()

# %% calculate deviation from the mean of each run
df1["deviation"] = df1["Temp[°C]"] - df1["Temp[°C]"].mean()
df2["deviation"] = df2["Temp[°C]"] - df2["Temp[°C]"].mean()

# %% calculate deviation from DWD station
df1["deviation_dwd"] = df1["Temp[°C]"] - df1["T"]
df2["deviation_dwd"] = df2["Temp[°C]"] - df2["T"]

# %% plot deviation from mean
plt.rc("font", size=16)
for i, df in enumerate([df1, df2]):
    plot_df = df  # [::10]  # subsample dataframe if needed
    fig, ax = plt.subplots(figsize=(6.9, 9), subplot_kw=dict(projection=request.crs))
    extent = [12.35, 12.43, 51.31, 51.4]  # (xmin, xmax, ymin, ymax)
    ax.set_extent(extent)
    ax.add_image(request, 12)
    scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["deviation_dwd"], transform=ccrs.Geodetic(),
                         cmap="inferno", vmin=-1, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Temperaturabweichung von Holzhausen (°C)")
    ax.set_title(f"Messfahrt 18. Juli 2022 - {plot_df.time.iloc[0]:%H:%M} - {plot_df.time.iloc[-1]:%H:%M} UTC")
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"{plot_path}/20220718_F46077A2930C_{i+1}_abweichung_holzhausen_karte.png", dpi=300, transparent=True)
    plt.close()

# %% PART 2: General Overview Tuesday and Wednesday, set paths
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

# dwd data
# dwd_df = station_temp("Holzhausen", pd.to_datetime("2022-07-19 00:00"), pd.to_datetime("2022-07-20 00:00"))

df = df[df.speed > 10]

# %% select time
start = pd.to_datetime("2022-07-19", utc=True)
end = pd.to_datetime("2022-07-21", utc=True)
df = df[(df.time >= start) & (df.time <= end)]

# %% plot four maps and time series
plt.rc("font", size=16)
starts = [pd.to_datetime("2022-07-19 13:00", utc=True), pd.to_datetime("2022-07-19 19:00", utc=True),
          pd.to_datetime("2022-07-20 13:00", utc=True), pd.to_datetime("2022-07-20 19:00", utc=True)]
ends = [pd.to_datetime("2022-07-19 15:00", utc=True), pd.to_datetime("2022-07-19 22:00", utc=True),
        pd.to_datetime("2022-07-20 15:00", utc=True), pd.to_datetime("2022-07-20 22:00", utc=True)]
for s, e in zip(starts, ends):
    plot_df = df[(df.time >= s) & (df.time <= e)]
    # map
    request = cimgt.OSM()
    fig, ax = plt.subplots(figsize=(7.5, 9), subplot_kw=dict(projection=request.crs))
    extent = [12.3, 12.45, 51.25, 51.4]  # (xmin, xmax, ymin, ymax)
    ax.set_extent(extent)
    ax.add_image(request, 12)
    scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["air_temperature"], transform=ccrs.Geodetic(),
                         cmap="inferno", vmin=17, vmax=40)
    cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Temperatur (°C)")
    ax.set_title(f"Messfahrt {s:%d} Juli 2022 - {plot_df.time.iloc[0]:%H:%M} - {plot_df.time.iloc[-1]:%H:%M} UTC")
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"{plot_path}/temperature_karte_{s:%Y%m%d_%H%M}-{e:%Y%m%d_%H%M}.png", dpi=300, transparent=True)
    plt.close()

# %% plot time series with maximum
df = df.sort_values(by="time")
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df.time, df.air_temperature, linewidth=4, label="MeteoTracker", color="#CC6677")
# ax.plot(df.time, df.T, linewidth=4, label="Holzhausen")
h.set_xticks_and_xlabels(ax, df.time.max() - df.time.min())
ax.grid()
max_temp = df[df.air_temperature == df.air_temperature.max()].iloc[0]
ax.annotate(f"Maximum: {df.air_temperature.max()}", xy=(max_temp.time, max_temp.air_temperature),
            xytext=(20, 3), textcoords="offset points", arrowprops=dict(facecolor='black', arrowstyle="simple"))
# max_temp = df[df.T == df.T.max()].iloc[0]
# ax.annotate(f"Maximum: {df.T.max()}", xy=(max_temp.time, max_temp.T),
#             xytext=(20, 3), textcoords="offset points", arrowprops=dict(facecolor='black', arrowstyle="simple"))
ax.set_xlabel("Zeit (UTC)")
ax.set_ylabel("Lufttemperatur (°C)")
ax.set_title(f"Temperaturverlauf {df.time.min():%d Juli} - {df.time.max():%d Juli} 2022")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/temperature_zeitreihe_{df.time.min():%Y%m%d_%H%M}-{df.time.max():%Y%m%d_%H%M}.png")
plt.close()
