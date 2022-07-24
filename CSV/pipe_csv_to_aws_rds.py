#  ________ CONVERT Pill CSV data to SQL _____________
import pandas as pd
import sqlite3
import psycopg2
from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite
from dotenv import load_dotenv
import os
load_dotenv()

def verify_output(pgres_engine, table_name):
    # ______  verify output-table contents ____
    query = 'SELECT * FROM ' +  table_name + ' LIMIT 10;'
    for row in pgres_engine.execute(query).fetchall():
        print(row)
    return

def run_conversion(engine):
    # ___ load the CSV into a df ____
    csv_url = "Pills.Final.csv"
    df = pd.read_csv(csv_url)
    print('CSV loaded successfully')
    # ___ process tables ____
    # - WARNING!  schema must already exist in AWS-RDS 
    #             when creating RDS database specify
    #             matching 'Initial database name" in Add'l Configuration panel
    #             create using pgAdmin
    schema_name = 'rxid'
    tables = ['rxid_meds_data']
    for table_name in tables:
        print('df.to_sql STARTED...table =', table_name)
        #  BUG ALERT! drop the dataframe index column
        #             before executing .to_sql()
        # ___ Convert to postgres DB____
        df.to_sql(table_name,
                  if_exists='replace',
                  con=engine,
                  schema=schema_name,
                  chunksize=1000,
                  index=False,
                  method='multi')
        print('df.to_sql COMPLETE....')
                   
        #_____  VERIFY _______________
        verify_output(engine, (schema_name + "." + table_name))
    return

def main():
    print('Conversion PIPELINE initiated at.....')

    # __ Connect to AWS-RDS(postgres) (SQLalchemy.create_engine) ____
    dbname = os.getenv("RDS_DB_NAME")
    user = os.getenv("RDS_DB_USER")
    host = os.getenv("RDS_DB_HOST")
    passw = os.getenv("RDS_DB_PASSWORD")
    pgres_str = 'postgresql+psycopg2://'+user+':'+passw+'@'+host+'/'+dbname
    print(pgres_str)
    pgres_engine = create_engine(pgres_str)
    print('pgres_engine created.....')
    # ____ Port CSV to AWS_RDS(postgres) ___
    run_conversion(pgres_engine)

    # ___ end main ___________
    print('Conversion PIPELINE successful.....')
    return

#  Launched from the command line
if __name__ == '__main__':
    main()