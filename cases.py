import requests
import json
import pandas as pd
import os
import sqlite3

# payload = {'code': 'ALL'}
# URL = 'https://api.statworx.com/covid'
# response = requests.post(url=URL, data=json.dumps(payload))

# if response.status_code == 200:
#     data = response.json()
#     # print(data)

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