#!/usr/bin/env python
# coding: utf-8

# In[5]: index


from wetterdienst import Wetterdienst
from wetterdienst.provider.dwd.observation import DwdObservationRequest, DwdObservationDataset, DwdObservationPeriod, DwdObservationResolution

from datetime import datetime, timedelta






import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import smopy


def station_temp(name, start_date, end_date):
    request = DwdObservationRequest(parameter=[DwdObservationDataset.TEMPERATURE_AIR],
                                resolution=DwdObservationResolution.MINUTE_10,
                                start_date=start_date,
                                end_date=end_date,
                                ).filter_by_name(name=name)

    df_res = request.values.all().df.dropna()

    df_Temp=df_res[df_res.parameter=="temperature_air_mean_200"].drop(['dataset', 'parameter', 'quality'], axis=1)
    df_Temp.rename(columns={'value':'T'}, inplace=True)
    df_dew=df_res[df_res.parameter=="temperature_dew_point_mean_200"].drop(['station_id', 'dataset', 'parameter', 'quality'], axis=1)
    
    df_dew.rename(columns={'value':'Td'}, inplace=True)
    
    df_Temp.set_index(pd.DatetimeIndex(df_Temp['date']), inplace=True)
    
    
    df_dew.set_index(pd.DatetimeIndex(df_Temp['date']), inplace=True)
    
    df_out=df_Temp.merge(df_dew, how='left', left_index=True, right_index=True)
    df_out["time"]=pd.to_datetime(df_Temp.date, format="%Y-%m-%d %H:%M:%S%z").dt.tz_localize(None)
    #df_out["SEC"]=pd.to_timedelta(df_Temp.date).dt.total_seconds()
    df_out.set_index(df_out["time"], inplace=True)
    #df_out.drop(["date"], axis=1)
    #df_out.set_index("time", inplace=True)
    df_out=df_out.drop(["date_x", "date_y"], axis=1)
    #df_out.T=df_out.T-273.15
    #df_out.Td=df_out.Td-273.15

    return df_out



# In[17]: Read file


station="Leipzig-Holzhausen"
#station="Leipzig/Halle"

fn = "./processed/2022-05-24_meteotracker.csv"

ds = pd.read_csv(fn)
#ds=ds[100:-100]
ds.time=pd.to_datetime(ds.time, format="%Y-%m-%dT%H:%M:%S.%fZ")


ds["hour"]=ds["time"].dt.strftime("%H").astype(int)



ds.set_index(pd.DatetimeIndex(ds["time"]), inplace=True)
print("Überblick zum Datensatz:")
print()
print(ds.nunique())
ds_raw=ds

ds=ds[ds.speed>10] # eliminiert Messungen bei Stillstand
print()
print()
print("gefiltert nach Geschwindigkeit:  ")
print()
print( ds.nunique())
# In[13]: plot raw map

map = smopy.Map((51.294, 12.31, 51.393, 12.42), z=12)

map.show_ipython()

#%%
start_date=datetime.strftime(min(ds.time), format="%Y-%m-%d")
end_date=datetime.strftime(max(ds.time)+np.timedelta64(1, 'D'), format="%Y-%m-%d")


DWD=station_temp(station, start_date, end_date)




# In[19]: add Dataset
ax = map.show_mpl(figsize=(15, 12))

x, y = map.to_pixels(ds.lat, ds.lon)


ax.set_title("Gemessene Temperaturen am "+start_date+ " in $^\circ C$", fontsize=30)

scatter=ax.scatter(x,y, c=ds.air_temperature, cmap="plasma")
cbar=plt.colorbar(scatter, ax=ax)

# In[19]: Zeitreihe:wann wurde gemessen?
ax = map.show_mpl(figsize=(10, 8))

x, y = map.to_pixels(ds.lat, ds.lon)


ax.set_title("Messzeiten am "+start_date+" in h", fontsize=20)

scatter=ax.scatter(x,y, c=ds.hour, cmap="rainbow")
plt.colorbar(scatter, ax=ax)









#%%
#ds["SOD"]=timedelta.seconds(ds.time-datetime.strptime(start_date, "%Y-%m-%d"))

#df_compared=ds.append(Holzhausen, sort=False)
df_compared=ds.merge(DWD, how="outer", sort=True, left_index=True, right_index=True)
#df_compared["SOD"]=pd.to_timedelta(df_compared.time).dt.total_seconds()

df_compared=df_compared.drop(["time_x", "time_y"], axis=1)
#df_compared.set_index("SEC", inplace=True)
#df_compared.set_index(pd.DatetimeIndex(df_compared['time']), inplace=True)
#df_compared=df_compared.drop("date", axis=1)
#for col in ["T", "Td"]:
 #   df_compared[col]=pd.to_numeric(df_compared[col], errors='coerce')
    
df_compared["T"]=df_compared["T"]-273.15
df_compared["Td"]=df_compared["Td"]-273.15
df_compared["T"]=df_compared["T"].interpolate(method="time", inplace=False, axis=0)
df_compared["Td"]=df_compared["Td"].interpolate(method="time", inplace=False, axis=0)
df_compared["T_diff"]=df_compared["air_temperature"]-df_compared["T"]


#%%

fig, ax=plt.subplots(figsize=(7, 4))
ax.plot(df_compared["air_temperature"], label="T Track")
ax.set_xlabel("Zeit")
ax.set_ylabel("Temperatur in $^\circ C$")
fig.suptitle("Zeitreihe Messfahrten"+ " am "+start_date)


#%%
fig, ax=plt.subplots(figsize=(7, 4))
ax.plot(df_compared["T"], label="T "+station)
fig.suptitle("T "+station+ " am "+start_date)
ax.set_xlabel("Zeit")
ax.set_ylabel("Temperatur in $^\circ C$")

#%%
fig, ax=plt.subplots(figsize=(7, 4))
ax.plot(df_compared["T"], label="T "+station)
ax.plot(df_compared["air_temperature"], label="T Track")
fig.suptitle("Zeitreihe Messfahrten und Tagesgang "+station+ " am "+start_date)
ax.set_xlabel("Zeit")
ax.set_ylabel("Temperatur in $^\circ C$")
ax.legend()



#%%
fig, ax=plt.subplots(figsize=(7, 4))
ax.plot(df_compared["T"], label="T "+station)
ax.plot(df_compared["air_temperature"], label="T Track")
fig.suptitle("Zeitreihe Messfahrten und Tagesgang "+station+ " am "+start_date)
ax.set_xlabel("Zeit")
ax.set_ylabel("Temperatur in $^\circ C$")
ax.grid()
ax.legend()

ax.set_xlim([min(ds.time),max(ds.time) ])

#%%
fig, ax=plt.subplots(figsize=(7, 4))
ax.plot(df_compared.T_diff)
fig.suptitle("Temperaturdifferenz Messfahrt - "+station)



# In[19]: add differential

ax = map.show_mpl(figsize=(10, 8))
x, y = map.to_pixels(df_compared.lat, df_compared.lon)


ax.set_title("Gemessene Temperaturdifferenzen ggü. "+station+ " am "+start_date, fontsize=20)
scatter=ax.scatter(x,y, c=df_compared.T_diff, cmap="seismic", vmin=-5, vmax=5)
plt.colorbar(scatter, ax=ax)

