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


# %% PART 1: General Overview Juli
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
dwd_df = station_temp("Holzhausen", pd.to_datetime("2022-07-01 00:00"), pd.to_datetime("2022-07-31 00:00"))

# %% select date range
df = df[df.time.dt.month == 7]  # select July only

# %% filter out values with speed below 10 km/h
df = df[df.speed > 10]

# %% calculate some statistics
at_mean, at_min, at_max = df.air_temperature.mean(), df.air_temperature.min(), df.air_temperature.max()

# %% get temperature distribution
plt.rc("font", size=16)
df.air_temperature.hist(bins=40, color="#CC6677", figsize=(10, 6))
plt.axvline(at_min, color="#0072B2", label=f"Minimum {at_min:2.1f} °C", linewidth=4)
plt.axvline(at_mean, color="#009E73", label=f"Mittelwert {at_mean:2.1f} °C", linewidth=4)
plt.axvline(at_max, color="#D55E00", label=f"Maximum {at_max:2.1f} °C", linewidth=4)
plt.xlabel("Temperatur (°C)")
plt.ylabel("Anzahl Messwerte")
plt.legend()
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/juli_temperaturverteilung.png", dpi=100)
plt.close()

# %% get temperature distribution of DWD station
at_mean, at_min, at_max = dwd_df["T"].mean(), dwd_df["T"].min(), dwd_df["T"].max()
plt.rc("font", size=16)
dwd_df["T"].hist(bins=40, color="#CC6677", figsize=(10, 6))
plt.axvline(at_min, color="#0072B2", label=f"Minimum {at_min:2.1f} °C", linewidth=4)
plt.axvline(at_mean, color="#009E73", label=f"Mittelwert {at_mean:2.1f} °C", linewidth=4)
plt.axvline(at_max, color="#D55E00", label=f"Maximum {at_max:2.1f} °C", linewidth=4)
plt.xlabel("Temperatur (°C)")
plt.ylabel("Anzahl Messwerte")
plt.legend()
plt.title("Temperatureverteilung Juli - Holzhausen")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/juli_temperaturverteilung_holzhausen.png", dpi=100)
plt.close()

# %% get time distribution
df.time.dt.hour.hist(bins=range(0, 25), color="#44AA99", figsize=(10, 6))
plt.xticks(range(25))
plt.xlabel("Uhrzeit (Stunde)")
plt.ylabel("Anzahl Messwerte")
plt.title("Zeitliche Verteilung der Messwerte")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/juli_messzeitverteilung.png", dpi=100)
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
plt.savefig(f"{plot_path}/juli_monatliche_stündliche_mittlere_temperatur.png", dpi=100)
plt.close()

# %% make a boxplot of temperature grouped by hour
df_1.boxplot("air_temperature", by="hour", figsize=(10, 6))
plt.xlabel("Uhrzeit (Stunde)")
plt.ylabel("Temperatur (°C)")
plt.title("Boxplot der Lufttemperatur")
plt.suptitle("")
plt.tight_layout()
# plt.show()
plt.savefig(f"{plot_path}/juli_stündliche_temperatur_boxplot.png", dpi=100)
plt.close()

# %% plot map of group measurement
plt.rc("font", size=16)
s = pd.to_datetime("2022-07-28 16:00", utc=True)
e = pd.to_datetime("2022-07-28 21:00", utc=True)
device_id = "F0:F8:F2:DA:CF:2F"
plot_df = df[(df.time >= s) & (df.time <= e)]
plot_df = plot_df[plot_df["device_id"] == device_id]
# map
request = cimgt.OSM()
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(projection=request.crs))
extent = [12.33, 12.44, 51.325, 51.375]  # (xmin, xmax, ymin, ymax)
ax.set_extent(extent)
ax.add_image(request, 13)
scatter = ax.scatter(plot_df["lon"], plot_df["lat"], c=plot_df["air_temperature"], transform=ccrs.Geodetic(),
                     cmap="inferno")
cbar = plt.colorbar(scatter, ax=ax, orientation="vertical", label="Temperatur (°C)")
ax.set_title(f"Messfahrt {s:%d} Juli 2022 - {plot_df.time.iloc[0]:%H:%M} - {plot_df.time.iloc[-1]:%H:%M} UTC")
plt.tight_layout()
plt.show()
# plt.savefig(f"{plot_path}/temperature_karte_{s:%Y%m%d_%H%M}-{e:%Y%m%d_%H%M}.png", dpi=300, transparent=True)
plt.close()


