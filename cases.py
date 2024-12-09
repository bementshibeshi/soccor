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
        # Convert the response data into a DataFrame
        df = pd.DataFrame.from_dict(json.loads(response.text)) 
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}, Reason: {response.reason}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of failure

    return df

def get_month(df):
    if 'date' in df.columns:
        # Convert the 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'])

        # Create a 'month' column to group data by month
        df['month'] = df['date'].dt.to_period('M')

        # Get the last day of each month for every country
        df_last_day_of_month = df.groupby(['month', 'country']).apply(
            lambda group: group[group['date'] == group['date'].max()]
        ).reset_index(drop=True)

        # Format the 'last_day_of_month' column
        df_last_day_of_month['last_day_of_month'] = df_last_day_of_month['date'].dt.strftime('%Y-%m-%d')

        # Keep only the relevant columns for display
        df_last_day_of_month = df_last_day_of_month[['last_day_of_month', 'country', 'code', 'cases']]  

        # Print the results with country and country codes
        print(df_last_day_of_month)
    else:
        print("The expected 'date' column is not present in the data.")

def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    return cur, conn

def update_country_codes(df, cur, conn):
    # Get unique country and country code pairs
    unique_countries = df[['country', 'code']].drop_duplicates()

    # Get existing countries from the database
    cur.execute("SELECT country FROM Countries")
    countries_in_db = cur.fetchall()
    countries_in_db = {country[0] for country in countries_in_db}

    # Add the 'country_code' column if it doesn't exist
    try:
        cur.execute('''ALTER TABLE Countries ADD COLUMN country_code TEXT''')
    except sqlite3.OperationalError:
        pass

    # Update the country codes in the database
    for _, row in unique_countries.iterrows():
        country_name = row['country']
        country_code = row['code']
        if country_name in countries_in_db:
            cur.execute('''UPDATE Countries SET country_code = ? WHERE country = ?''', (country_code, country_name))
    
    conn.commit()

def main():
    df = get_df()
    if not df.empty:
        get_month(df)

        # Set up the database and update country codes
        cur, conn = set_up_database("206_final.db")
        update_country_codes(df, cur, conn)

        conn.close()
    else:
        print("No data to process.")

if __name__ == "__main__":
    main()