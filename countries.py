import unittest
import sqlite3
import json
import os
import requests
import pprint


def get_country_ids():
    API_KEY = "376c8e51eb476474a720377fd3c9c83c"
    page1_url = f"https://api.soccersapi.com/v2.2/countries/?user=yeajee&token={API_KEY}&t=list&page=1"
    page2_url = f"https://api.soccersapi.com/v2.2/countries/?user=yeajee&token={API_KEY}&t=list&page=2"
    # headers = {"Authorization": f"Bearer {API_KEY}"}
    
    resp1 = requests.get(page1_url)
    resp2 = requests.get(page2_url)

    # print(resp1, resp2)

    if resp1.status_code == 200 and resp2.status_code == 200:
        data1 = resp1.json()
        data2 = resp2.json()

        countries = data1.get("data", [])
        countries2 = data2.get("data", [])
        country_data = [{"id": country["id"], "name": country["name"]} for country in countries]
        country_data2 = [{"id": country["id"], "name": country["name"]} for country in countries2]

        # print("This is page 1:", 
              
        #       country_data)
        # print("This is page 2:"
              
        #       , country_data2)

        country_data.extend(country_data2)
        print(country_data)

        return country_data
    else:
        print(f"Error: {resp1.status_code} - {resp1.reason}")
        return None


def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn


def set_up_countries_table(data, cur, conn):
    # Drop and create Countries table
    cur.execute("DROP TABLE IF EXISTS Countries")
    cur.execute("CREATE TABLE IF NOT EXISTS Countries (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")

    # Insert country data into the table
    for country in data:
        cur.execute(
            "INSERT OR IGNORE INTO Countries (id, name) VALUES (?, ?)", (country["id"], country["name"])
        )
    conn.commit()


def main():
    # Fetch country IDs and names
    country_data = get_country_ids()
    if not country_data:
        print("No country data retrieved. Exiting.")
        return

    # Setup database and insert data
    cur, conn = set_up_database("206_final.db")
    set_up_countries_table(country_data, cur, conn)
    conn.close()


if __name__ == "__main__":
    main()