import requests
import json
import pandas as pd
from datetime import datetime
import sqlite3
import os
import matplotlib.pyplot as plt

def get_df():
    """
    Fetches COVID-19 data from the Statworx API.

    Returns:
        pd.DataFrame: A DataFrame containing COVID-19 data for all countries, 
        or an empty DataFrame if the request fails.
    """
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
    """
    Sets up the SQLite database connection and enables foreign keys.

    Args:
        db_name (str): The name of the SQLite database file.

    Returns:
        tuple: A tuple containing the cursor and connection objects.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    return cur, conn

def update_country_codes(df, cur, conn):
    """
    Updates the 'Countries' table with country codes from the DataFrame.

    Args:
        df: A DataFrame containing country and code data.
        cur: Cursor object for database operations.
        conn: Connection object for the database.
    """

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
    """
    Filters the DataFrame to include only countries with matched codes in the database.

    Args:
        df (pd.DataFrame): A DataFrame containing country and code data.
        cur: Cursor object for database operations.

    Returns:
        pd.DataFrame: A filtered DataFrame with matched country codes.
    """
    cur.execute("SELECT country_code FROM Countries WHERE country_code IS NOT NULL")
    country_codes = cur.fetchall()
    country_codes = {code[0] for code in country_codes}

    matched_df = df[df['code'].isin(country_codes)]

    # print(matched_df)
    return matched_df

def get_month(matched_df):
    """
    Processes the DataFrame to extract the last day of each month's data for 2020.

    Args:
        matched_df: A DataFrame containing matched country data.

    Returns:
        pd.DataFrame: A DataFrame with data for the last day of each month in 2020.
    """
    if 'date' in matched_df.columns:
        matched_df['date'] = pd.to_datetime(matched_df['date'])

        df_2020 = matched_df[matched_df['date'].dt.year == 2020]

        df_2020['month'] = df_2020['date'].dt.to_period('M')

        df_last_day_of_month = df_2020.sort_values('date').groupby(['month', 'country'], as_index=False).last()

        df_last_day_of_month['last_day_of_month'] = df_last_day_of_month['date'].dt.strftime('%Y-%m-%d')
        df_last_day_of_month = df_last_day_of_month[['last_day_of_month', 'country', 'code', 'cases']]  

        df_last_day_of_month = df_last_day_of_month.sort_values(by=['country', 'last_day_of_month']).reset_index(drop=True)

        print(df_last_day_of_month)

    else:
        print("The expected 'date' column is not present in the data.")

    return df_last_day_of_month

def insert_df_into_db(df, cur, conn):
    """
    Inserts a DataFrame into the 'Cases' table in the database.

    Args:
        df (pd.DataFrame): A DataFrame containing cases data.
        cur: Cursor object for database operations.
        conn: Connection object for the database.
    """

    cur.execute(f"DROP TABLE IF EXISTS Cases")

    cur.execute(f'''
        CREATE TABLE Cases (
            last_day_of_month TEXT,
            country TEXT,
            code TEXT,
            cases INTEGER
        )
    ''')

    for _, row in df.iterrows():
        cur.execute(f'''
            INSERT INTO Cases (last_day_of_month, country, code, cases)
            VALUES (?, ?, ?, ?)
        ''', (row['last_day_of_month'], row['country'], row['code'], row['cases']))

    conn.commit()


def visualize_cases(df):
    if not df.empty:
        df['last_day_of_month'] = pd.to_datetime(df['last_day_of_month'])

        total_cases_per_country = df.groupby('country')['cases'].sum()

        top_10_countries = total_cases_per_country.sort_values(ascending=False).head(10)

        plt.figure(figsize=(10, 10))
        colors = plt.cm.Paired(range(len(top_10_countries)))  # Adjust colors for the top 10 countries
        top_10_countries.plot.pie(
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            fontsize=10,
            legend=False
        )
        plt.ylabel('')
        plt.title("Top 10 Countries with the Most COVID-19 Cases", fontsize=14)
        plt.tight_layout()
        plt.show()

    else:
        print("The DataFrame is empty. Cannot visualize data.")


def main():
    df = get_df()
    if not df.empty:
        cur, conn = set_up_database("206_final.db")
        update_country_codes(df, cur, conn)

        matched_df = get_matched_data(df, cur)
        print("Matched Data:")

        casesdf = get_month(matched_df)

        insert_df_into_db(casesdf, cur, conn)

        visualize_cases(casesdf)

        conn.close()
    else:
        print("No data to process.")

if __name__ == "__main__":
    main()
