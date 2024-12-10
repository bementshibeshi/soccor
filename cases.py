import requests
import json
import pandas as pd
from datetime import datetime
import sqlite3
import os
import matplotlib.pyplot as plt

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

    # print(matched_df)
    return matched_df

def get_month(matched_df):
    
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

import seaborn as sns
def visualize_cases(df):
    if not df.empty:
        # Ensure 'last_day_of_month' is datetime
        df['last_day_of_month'] = pd.to_datetime(df['last_day_of_month'])

        # Group by 'last_day_of_month' and 'country', summing the cases
        grouped_df = df.groupby(['last_day_of_month', 'country']).agg({'cases': 'sum'}).reset_index()

        # Create a pivot table for easier plotting
        pivot_df = grouped_df.pivot(index='last_day_of_month', columns='country', values='cases')

        # Calculate the total cases for each country
        total_cases_per_country = pivot_df.sum().sort_values(ascending=False)

        # Select the top 3 countries
        top_3_countries = total_cases_per_country.head(3).index

        # Filter the pivot table to include only the top 3 countries
        top_3_df = pivot_df[top_3_countries]

        # Set up the color palette
        palette = sns.color_palette("tab10", len(top_3_df.columns))  # Adjust colors for the top 3 countries

        # Plot
        ax = top_3_df.plot(kind='bar', stacked=False, figsize=(14, 8), color=palette, width=0.8)
        ax.set_title("Top 3 Countries with the Most COVID-19 Cases by Date", fontsize=16)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Total Cases", fontsize=12)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")  # Rotate x labels for better readability

        # Display legend
        plt.legend(title='Countries', bbox_to_anchor=(1.05, 1), loc='upper left')

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