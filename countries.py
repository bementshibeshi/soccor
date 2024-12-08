import unittest
import sqlite3
import json
import os
import requests
import pprint


def get_country_ids():
    API_KEY = "376c8e51eb476474a720377fd3c9c83c"
    team_url = "https://api.soccersapi.com/v2.2/teams/?user=null&token=null&t=list&country_id=4"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    resp = requests.get(team_url, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()

        # Extract country IDs and names
        countries = data.get("data", [])
        country_data = [{"id": country["id"], "name": country["name"]} for country in countries]
        return country_data
    else:
        print(f"Error: {resp.status_code} - {resp.reason}")
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