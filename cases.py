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

        df = pd.DataFrame.from_dict(json.loads(response.text)) 
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}, Reason: {response.reason}")
        df = pd.DataFrame() 

    return df

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
        country_code = row['code']
        if country_name in countries_in_db:
            cur.execute('''UPDATE Countries SET country_code = ? WHERE country = ?''', (country_code, country_name))
    
    conn.commit()

def get_matched_data(df, cur):
    cur.execute("SELECT country_code FROM Countries WHERE country_code IS NOT NULL")
    country_codes = cur.fetchall()
    country_codes = {code[0] for code in country_codes}

    matched_df = df[df['code'].isin(country_codes)]

    print(matched_df)
    return matched_df

def get_month(matched_df):
    if 'date' in matched_df.columns:
        matched_df['date'] = pd.to_datetime(matched_df['date'])

        # Filter data for the year 2020
        df_2020 = matched_df[matched_df['date'].dt.year == 2020]

        # Generate a month period and create an auxiliary column 'month'
        df_2020['month'] = df_2020['date'].dt.to_period('M')

        # Find the last day of the month by grouping by 'month' and 'country'
        df_last_day_of_month = df_2020.sort_values('date').groupby(['month', 'country'], as_index=False).last()

        # Ensure we're only capturing the required columns
        df_last_day_of_month['last_day_of_month'] = df_last_day_of_month['date'].dt.strftime('%Y-%m-%d')
        df_last_day_of_month = df_last_day_of_month[['last_day_of_month', 'country', 'code', 'cases']]  

        # Sort the result for readability
        df_last_day_of_month = df_last_day_of_month.sort_values(by=['country', 'last_day_of_month']).reset_index(drop=True)

        print(df_last_day_of_month)

    else:
        print("The expected 'date' column is not present in the data.")

    return df_last_day_of_month

def main():
    df = get_df()
    if not df.empty:
        cur, conn = set_up_database("206_final.db")
        update_country_codes(df, cur, conn)

        matched_df = get_matched_data(df, cur)
        print("Matched Data:")

        get_month(matched_df)

        conn.close()
    else:
        print("No data to process.")

if __name__ == "__main__":
    main()