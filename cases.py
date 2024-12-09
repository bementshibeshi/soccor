import requests
import json
import pandas as pd
<<<<<<< HEAD
from datetime import datetime
=======
import os
import sqlite3
>>>>>>> 8bc3b2acf4c1350640d2e7b598eaaf15471d7798

# payload = {'code': 'ALL'}
# URL = 'https://api.statworx.com/covid'
# response = requests.post(url=URL, data=json.dumps(payload))

# if response.status_code == 200:
#     data = response.json()
#     # print(data)

<<<<<<< HEAD
    # Convert the response data to a DataFrame
    df = pd.DataFrame.from_dict(json.loads(response.text)) 

    # Check if the DataFrame contains the necessary columns
    if 'date' in df.columns:
        # Convert 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'])

        # Extract the year and month for easier filtering
        df['month'] = df['date'].dt.to_period('M')  # This will give 'YYYY-MM' format

        # Now, get the last record for each country per month
        df_last_day_of_month = df.groupby(['month', 'country']).apply(lambda group: group[group['date'] == group['date'].max()]).reset_index(drop=True)

        # Create a column for the last day of the month (this will be the last date from 'date' column)
        df_last_day_of_month['last_day_of_month'] = df_last_day_of_month['date'].dt.strftime('%Y-%m-%d')

        # Drop unnecessary columns
        df_last_day_of_month = df_last_day_of_month[['last_day_of_month', 'country', 'cases']]  # Keep only the last_day_of_month, country, and cases columns

        # Display the result for the last day of each month for every country
        print(df_last_day_of_month)
    else:
        print("The expected 'date' column is not present in the data.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}, Reason: {response.reason}")
=======
#     country = data['country']
#     total_cases = data['cases']

#     df = pd.DataFrame({'Country': [country], 'Total Cases': [total_cases]})

#     print(df)
# else:
#     print(f"Failed to fetch data. Status code: {response.status_code}, Reason: {response.reason}")

def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    return cur, conn

def get_code(cur, conn):

    cur.execute("""SELECT country from Countries""")
    countries = cur.fetchall()
    print(countries)

    payload = {'code': 'ALL'}
    URL = 'https://api.statworx.com/covid'
    response = requests.post(url=URL, data=json.dumps(payload))
    
    if response.status_code == 200:
        data = response.json()
        countrylist = []

        for country in data:
            country_name = country.get("name")
            country_code = country.get("code")
            if country_name and country_code:
                countrylist.append((country_name, country_code))
        
        print(countrylist)

        cur.execute('''ALTER TABLE Countries ADD COLUMN country_code TEXT''')

        for country_name, country_code in countrylist:

            cur.execute(
                '''UPDATE Countries SET country_code = ? WHERE country = ?''', (country_code, country_name)
            )

        conn.commit()

def main():
    cur, conn = set_up_database("206_final.db")
    get_code(cur, conn)
    conn.close()

if __name__ == "__main__":
    main()
>>>>>>> 8bc3b2acf4c1350640d2e7b598eaaf15471d7798
