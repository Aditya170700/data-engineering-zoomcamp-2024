import pandas as pd
import argparse
import os
from time import time
from sqlalchemy import create_engine

def main(params):
  user = params.user
  password = params.password
  host = params.host
  port = params.port
  dbname = params.dbname
  url = params.url
  table = params.table
  
  if url.endswith('.csv.gz'):
    csv_name = 'output.csv.gz'
  else:
    csv_name = 'output.csv'
  
  # download dataset
  os.system(f'wget {url} -O {csv_name}')
  
  # format url : 'postgresql://[user]:[password]@[host]:[port]/[dbname]'
  engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{dbname}')

  # Membagi data dalam chunk
  df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

  # dapatkan chunk pertama dan simpan ke variabel df
  df=next(df_iter)
  
  # ubah kolom tpep_pickup_datetime dan tpep_dropoff_datetime (string -> datetime) pake pandas.to_datetime
  df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
  df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

  # head(n=0), ambil data paling atas (kalo scv biasanya nama-nama kolom)
  df.head(n=0).to_sql(name=table, con=engine, if_exists='replace')
  
  # simpan dataframe ke tabel
  df.to_sql(name=table, con=engine, if_exists='append')

  #loop akan berjalan sampai terjadi exception seperti StopIteration
  while True:
    try:
      t_start = time()
      
      # mengambil next chunk dari df_iter
      df = next(df_iter)

      # ubah kolom tpep_pickup_datetime dan tpep_dropoff_datetime (string -> datetime) pake pandas.to_datetime
      df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
      df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

      # simpan dataframe ke tabel
      df.to_sql(name=table, con=engine, if_exists='append')

      t_end = time()

      print('inserted another chunk, took %.3f second' % (t_end - t_start))
    except StopIteration:
      print('Finished ingesting data into the postgres database')
      break

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

  parser.add_argument('--user', required=True, help='user for postgres connection')
  parser.add_argument('--password', required=True, help='password for postgres connection')
  parser.add_argument('--host', required=True, help='host for postgres connection')
  parser.add_argument('--port', required=True, help='port for postgres connection')
  parser.add_argument('--dbname', required=True, help='dbname for postgres connection')
  parser.add_argument('--url', required=True, help='url for raw data')
  parser.add_argument('--table', required=True, help='table for postgres connection')
  
  args = parser.parse_args()
  
  main(args)
