from haversine import haversine
import pandas as pd


def pmc_midrange(df, error_bound):
    current_lat = df["latitude"].iloc[0]
    current_lon = df["longitude"].iloc[0]
    list_taxi_id = [df["taxi_id"].iloc[0]]
    list_start_time = [df["datetime"].iloc[0]]
    list_longitude = [df["longitude"].iloc[0]]
    list_latitude = [df["latitude"].iloc[0]]
    list_end_time = []
    list_counter = []
    counter = 1

    for i, row in df.iterrows():
        if haversine((current_lat, current_lon), (row["latitude"], row["longitude"])) > error_bound:
            list_end_time.append(df["datetime"].iloc[i-1])
            list_counter.append(counter)

            list_taxi_id.append(row["taxi_id"])
            list_start_time.append(row["datetime"])
            list_longitude.append(row["longitude"])
            list_latitude.append(row["latitude"])
            current_lat = df["latitude"].iloc[i]
            current_lon = df["longitude"].iloc[i]
            counter = 1
        else:
            counter += 1
    list_end_time.append(df["datetime"].iloc[-1])
    list_counter.append(counter)

    list_concat = {
        "taxi_id": list_taxi_id,
        "start_time": list_start_time,
        "longitude": list_longitude,
        "latitude": list_latitude,
        "counter": list_counter,
        "end_time": list_end_time
    }

    pmc_df = pd.DataFrame(list_concat)
    return pmc_df
