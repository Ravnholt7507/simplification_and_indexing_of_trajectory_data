from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from DOTS.DOTS import Node, LayeredDAG
import pandas as pd
import time

def dots(df, error_bound, multiplier):
    start_time = time.time()

    data_points = []
    for index, row in df.iterrows():
        data_points.append((index + 1, row["longitude"], row["latitude"], row["datetime"]))

    dag = LayeredDAG()
    dag.run_dots(data_points, error_bound, multiplier)
    data_points = dag.decode_trajectory()

    dag_df = pd.DataFrame(data_points, columns=['taxi_id', 'longitude', 'latitude', 'datetime'])
    dag_df = dag_df[['taxi_id', 'datetime', 'longitude', 'latitude']]

    end_time = time.time()
    print("DOTS time: ", end_time-start_time)
    return dag_df
