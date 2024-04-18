from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from DOTS.DOTS import Node, LayeredDAG
import pandas as pd

def dots(df, error_bound, multiplier):

    data_points = []
    for index, row in df.iterrows():
        data_points.append((index + 1, row["longitude"], row["latitude"], row["datetime"]))

    dag = LayeredDAG()
    dag.run_dots(data_points, error_bound, multiplier)
    data_points = dag.decode_trajectory()

    dag_df = pd.DataFrame(data_points, columns=['taxi_id', 'longitude', 'latitude', 'datetime'])
    dag_df = dag_df[['taxi_id', 'datetime', 'longitude', 'latitude']]

    return dag_df
