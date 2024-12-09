import requests
import json
import pandas as pd
from datetime import datetime
import sqlite3
import os

def get_df():

    payload = {'code': 'ALL'}
    URL = 'https://api.statworx.com/covid'
    response = requests.post(url=URL, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        # print(data)

        df = pd.DataFrame.from_dict(json.loads(response.text)) 
        # print(df)

    else:
            print(f"Failed to fetch data. Status code: {response.status_code}, Reason: {response.reason}")

    return df

def get_month(df):
        if 'date' in df.columns:

            df['date'] = pd.to_datetime(df['date'])

            df['month'] = df['date'].dt.to_period('M') 

            df_last_day_of_month = df.groupby(['month', 'country']).apply(lambda group: group[group['date'] == group['date'].max()]).reset_index(drop=True)

            df_last_day_of_month['last_day_of_month'] = df_last_day_of_month['date'].dt.strftime('%Y-%m-%d')

            df_last_day_of_month = df_last_day_of_month[['last_day_of_month', 'country', 'cases']]  

            print(df_last_day_of_month)
        else:
            print("The expected 'date' column is not present in the data.")\
            
def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    return cur, conn
        
def update_country_codes(df, cur, conn):

    unique_countries = df[['country', 'code']].drop_duplicates()

    cur.execute("SELECT country FROM Countries")
    countries_in_db = cur.fetchall()
    countries_in_db = {country[0] for country in countries_in_db}

    try:
        cur.execute('''ALTER TABLE Countries ADD COLUMN country_code TEXT''')

    except sqlite3.OperationalError:
        pass

    for _, row in unique_countries.iterrows():
        country_name = row['country']
        print(country_name)
        country_code = row['code']
        if country_name in countries_in_db:
            cur.execute('''UPDATE Countries SET country_code = ? WHERE country = ?''', (country_code, country_name))
    
    conn.commit()
    
def main():
    df = get_df()
    get_month(df)

    cur, conn = set_up_database("206_final.db")
    update_country_codes(df, cur, conn)

    conn.close()

if __name__ == "__main__":
    main()