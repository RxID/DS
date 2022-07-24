#  ________ CONVERT Pill CSV data to SQL _____________
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import os
from dotenv import load_dotenv
load_dotenv()


def verify_output(pgres_engine, table_name):
    # ______  verify output-table contents ____
    query = 'SELECT * FROM ' + table_name + ' LIMIT 10;'
    for row in pgres_engine.execute(query).fetchall():
        print(row)
    return


def run_conversion(engine):
    # ___ load the CSV into a df ____
    csv_url = "Pills.Final.csv"
    df = pd.read_csv(csv_url)
    print('CSV loaded successfully')
    # ___ process tables ____
    # - WARNING!  schema must already exist, create schemas using pgAdmin
    #        In AWS-RDS, when creating RDS database, specify 
    #        'Initial database name" in Add'l Configuration panel to match RDS_DB_NAME
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

    # __ Connect to postgres  (SQLalchemy.create_engine) ____
    dbname = os.getenv("LOCAL_DB_NAME")
    user   = os.getenv("LOCAL_DB_USER")
    host   = os.getenv("LOCAL_DB_HOST")
    port   = os.getenv("LOCAL_DB_PORT")
    passw  = urllib.parse.quote_plus(os.getenv("LOCAL_DB_PASSWORD"))  # converts any special characters in password
    pgres_str = 'postgresql+psycopg2://'+user+':'+passw+'@'+host+':'+port+'/'+ dbname
    print(pgres_str)
    pgres_engine = create_engine(pgres_str)
    print('pgres_engine created.....')
    
    # ____ Port CSV to postgres ___
    run_conversion(pgres_engine)

    # ___ end main ___________
    print('Conversion PIPELINE successful.....')
    return


#  Launched from the command line
if __name__ == '__main__':
    main()
