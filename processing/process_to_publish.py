#!/usr/bin python3
"""
| *author*: Janosch Walde, Johannes Röttenbacher
| *date*: 14-10-2022

Prepare data for publishing:

- filter data to the Leipzig area
- create session IDs
- remove last 50 points from each session to anonymize the data
- drop sessions with less than 5 measurements
- create new session IDs
- write a daily csv file

"""

if __name__ == '__main__':
    # %% import modules
    import meteohautnah.meteohautnah as mh
    import pandas as pd
    from tqdm import tqdm

    # %% define paths
    base_dir = "C:/Users/Johannes/Documents/MeteorologieHautnah/MeteorologieHautnah"
    # base_dir = "/home/janosch/Dokumente/MeteorologieHautnah"  # Janosch
    data_path = f"{base_dir}/Daten/processed/"
    output_path = f"{base_dir}/Daten/v1.0"
    # date = "2022-05-03"  # "2022-05-18"  # yyyy-mm-dd or all
    dates = list(pd.date_range("2022-05-01", "2022-10-18").strftime("%Y-%m-%d"))  # which dates to save

    # %% read in data
    df = mh.read_data(data_path, "all", speedfilter=0)

    # %% filter data by location (Leipzig)
    lon_min, lon_max, lat_min, lat_max = 12.2, 12.55, 51.16, 51.45
    location_selection = (df.lon.between(lon_min, lon_max)) & (df.lat.between(lat_min, lat_max))
    df = df[location_selection].copy()

    # %% create session id for whole dataset
    df = mh.create_session_id(df)

    # %% remove last 50 points of each session to anonymize the data
    df = mh.remove_last_points_from_session(df, 50)

    # %% drop sessions which only consist of five rows/entries
    df = mh.drop_short_sessions(df, 5)

    # %% create new session ids after dropping sessions
    df = mh.create_session_id(df)
    date_str = df.time.dt.strftime("%Y-%m-%d")  # create series of dates for writing to csv files

    # %% write daily csv files
    for d in tqdm(dates):
        df_out = df[d == date_str]
        df_out.to_csv(f"{output_path}/{d}_meteotracker.csv", index=False, date_format="%Y-%m-%d %H:%M:%S%z")



