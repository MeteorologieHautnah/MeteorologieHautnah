#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 19:03:02 2022

@author: jakob
Takes downloaded csv-files and generates a animated clip.
2022-09-15: Skales changed for colder temperatures
"""

#%% Setup


from matplotlib import animation
import numpy as np
import multiprocessing as mp
import logging
logger = mp.log_to_stderr(logging.INFO)
import time
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
import os
import datetime
import matplotlib as mpl
import subprocess


from wetterdienst import Wetterdienst
from wetterdienst.provider.dwd.observation import DwdObservationRequest, DwdObservationDataset, DwdObservationPeriod, DwdObservationResolution

from datetime import datetime, timedelta
import datetime as dt




import pandas as pd

import smopy
import os


"""
import tempfile

tempfile.tempdir = "/projekt_agmwend/data/EUREC4A/11_VELOX-Tools/VELOX_Video/temp"
print(tempfile.gettempdir())
"""



# routine, um DWD-Stationsdaten komplett einzulesen

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

#Maniküre:


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 0, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()



##film update

def update(i, ax, ax2, ax3, temp_scatter, diff_scatter):
    #print('''update the image''')
    #logger.info( 'Updating frame %d'%i )
    
    global df_compared, DWD
    
    timestep=DWD.index[i]
    timeend=timestep+timedelta(hours=2)
    ax.clear()
    ax2.clear()

    ax3.clear()
    
    
    ax_map = map.show_mpl(ax=ax)

    x, y = map.to_pixels(df_compared.lat[timestep:timeend], df_compared.lon[timestep:timeend])
    
    
    fig.suptitle("Trackerdaten der letzten 2 Stunden um " +datetime.strftime(timeend, format="%Y-%m-%d %H:%M"), fontsize=20)
    #diff_scatter=ax.scatter(x,y, c=df_compared.T_diff[timestep:timeend], cmap="seismic", vmin=-5, vmax=5, s=2)
    diff_scatter=ax.scatter(x,y, c=df_compared.T_diff[timestep:timeend], cmap="Spectral_r", vmin=-4, vmax=4, s=2)
    ax.set_xlim(0, 775)
    ax.set_ylim(775, 0)
    ax.axis("off")

    
    ax.set_title("Differenz ggü. "+station+" in K")
    
    
    ax2_map = map.show_mpl(ax=ax2)
    x, y = map.to_pixels(df_compared.lat[timestep:timeend], df_compared.lon[timestep:timeend])
    
    temp_scatter=ax2.scatter(x,y, c=df_compared.air_temperature[timestep:timeend], cmap="plasma", vmin=5, vmax=30, s=2)
    
    ax2.set_title("gemessene Temperaturen in  $^\circ C$")
    ax2.set_xlim(0, 775)
    ax2.set_ylim(775, 0)
    ax2.axis("off")
    ax2.set_title("gemessene Temperaturen in  $^\circ C$")

    
    day_i=timestep-timedelta(hours=12)
    day_f=timestep+timedelta(hours=12)
    
    ax3.plot(df_compared["T"][day_i: day_f], label="T station")
    ax3.scatter(df_compared["time_x"][day_i: day_f], df_compared["air_temperature"][day_i: day_f], label="T Tracker", s=1, marker="+", color="red")
    
    ax3.set_title("Vergleich mit "+station)

    ax3.set_xlabel("Zeit")
    ax3.set_ylabel("Temperatur in $^\circ C$")
    ax3.grid()
    ax3.axvline(timestep, color='black')
    ax3.legend(loc="upper left")
    ax3.axvline(timeend, color='black')    
    
    printProgressBar(i + 1, DWD.index.shape[0] , prefix = 'Rendering:', suffix = 'Complete', length = 50)
    
   
    
    
    
    
   
    return diff_scatter




#%% Start of main programm


# %% define paths
data_path = "/projekt_agmwend/data/meteorologie_hautnah/daily_csv/"
plot_path = "/projekt_agmwend/data/meteorologie_hautnah/plots/"
date = "2022-09"  # "2022-05-18"  # yyyy-mm-dd or all
files = os.listdir(data_path)

files_filtered=[file for file in files if (date in file)]
# %% read in data

if date == "all":
    
    ds = pd.concat([pd.read_csv(f"{data_path}/{file}") for file in files])

else:
    ds = pd.concat([pd.read_csv(f"{data_path}/{file}") for file in files_filtered])
    
    
"""if date == "Mai":
    ds = pd.concat([pd.read_csv(f"{data_path}/{file}") for file in files if "2022-05" in file])
if date=="Juni":
    ds = pd.concat([pd.read_csv(f"{data_path}/{file}") for file in files if "2022-06" in file])
"""

"""else:
    file = [f for f in files if date in f][0]
    ds = pd.read_csv(f"{data_path}/{file}")
"""







#  Read file



station="Leipzig-Holzhausen"
#station="Leipzig/Halle"

#fn = "./processed/2022-05-24_meteotracker.csv"

#ds = pd.read_csv(fn)
#ds=ds[100:-100]
ds.time=pd.to_datetime(ds.time, format="%Y-%m-%dT%H:%M:%S.%fZ")


#ds["hour"]=ds["time"].dt.strftime("%H").astype(int)



ds.set_index(pd.DatetimeIndex(ds["time"]), inplace=True)

ds=ds.sort_index(axis=0)

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


#%%
#ds["SOD"]=timedelta.seconds(ds.time-datetime.strptime(start_date, "%Y-%m-%d"))

#df_compared=ds.append(Holzhausen, sort=False)
df_compared=ds.merge(DWD, how="outer", sort=True, left_index=True, right_index=True)
#df_compared["SOD"]=pd.to_timedelta(df_compared.time).dt.total_seconds()

df_compared=df_compared.drop(["time_y"], axis=1)
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

timestep=DWD.index[0]
timeend=timestep+timedelta(hours=2)
fig = plt.figure(figsize=(10,7))

ax=fig.add_axes([0, 0, 0.66, 0.9])
ax2=fig.add_axes([0.6, 0.5, 0.4, 0.4])
ax3=fig.add_axes([0.68, 0.1, 0.3, 0.35])

ax_map = map.show_mpl(ax=ax)
x, y = map.to_pixels(df_compared.lat[timestep:timeend], df_compared.lon[timestep:timeend])


fig.suptitle("Trackerdaten der letzten 2 Stunden um " +datetime.strftime(timeend, format="%Y-%m-%d %H:%M"), fontsize=20)
diff_scatter=ax.scatter(x,y, c=df_compared.T_diff[timestep:timeend], cmap="Spectral_r", vmin=-4, vmax=4, s=2)
ax.set_xlim(0, 775)
ax.set_ylim(775, 0)
ax.axis("off")

ax.set_title("Differenz ggü. "+station+" in K")
plt.colorbar(diff_scatter, ax=ax)


ax2_map = map.show_mpl(ax=ax2)
x, y = map.to_pixels(df_compared.lat[timestep:timeend], df_compared.lon[timestep:timeend])

temp_scatter=ax2.scatter(x,y, c=df_compared.air_temperature[timestep:timeend], cmap="plasma", vmin=5, vmax=30, s=2)
plt.colorbar(temp_scatter, ax=ax2)
ax2.set_title("gemessene Temperaturen in  $^\circ C$")
ax2.set_xlim(0, 775)
ax2.set_ylim(775, 0)
ax2.axis("off")


day_i=timestep-timedelta(hours=12)
day_f=timestep+timedelta(hours=12)

ax3.plot(df_compared["T"][day_i: day_f], label="T "+station)
ax3.scatter(df_compared["time_x"][day_i: day_f], df_compared["air_temperature"][day_i: day_f], label="Messungen Meteotracker", s=1, marker="+", color="red")
ax3.set_title("Vergleich mit "+station)
ax3.set_xlabel("Zeit")
ax3.set_ylabel("Temperatur in $^\circ C$")
ax3.grid()
ax3.axvline(timestep, color='black')
ax3.axvline(timeend, color='black')
ax3.legend(loc="lower right")


#%%


ani = FuncAnimation(fig,
                              update, frames=range(DWD.index.shape[0]),
                              fargs=( ax, ax2, ax3, temp_scatter, diff_scatter),
                              #init_func=init_func,
                              interval=(1000.0/6.0))

ani.save(plot_path+date+".mp4", dpi=300,)


