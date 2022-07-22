import pandas as pd
import sys

sys.path.append('../')


df = pd.read_parquet('data_files/db_cache.parquet')
df.to_csv('data_files/vehicle_cache.csv')