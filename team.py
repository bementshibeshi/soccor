import unittest
import sqlite3
import json
import os
import requests
import pprint
import matplotlib.pyplot as plt


def get_comp_id():
    """
    Fetches teams for each competition ID and organizes them by their country.
    
    Args:
        comp_ids (list): A list of competition IDs.
        
    Returns:
        dict: A dictionary where keys are country names and values are lists of team short names
              associated with that country.
    """
    API_KEY = "0cd173cf1b864ce092037aec02a7fdcb"
    team_url = "http://api.football-data.org/v4/competitions/"
    headers = {"X-Auth-Token": API_KEY}
    
    resp = requests.get(team_url, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        
        competitions = data.get("competitions", [])
        
        comp_ids = [comp["id"] for comp in competitions if "id" in comp]
        
        # print(comp_ids)
        return comp_ids
    else:
        print(f"Error: {resp.status_code} - {resp.reason}")
        return None


def get_comp_teams(comp_ids):
    """
    Fetches teams for each competition ID and organizes them by their country.
    
    Args:
        comp_ids (list): A list of competition IDs.
        
    Returns:
        dict: A dictionary where keys are country names and values are lists of team short names
              associated with that country.
    """
    API_KEY = "0cd173cf1b864ce092037aec02a7fdcb"
    countryteams = {}

    for comp_id in comp_ids:
        team_url = f"http://api.football-data.org/v4/competitions/{comp_id}/teams"
        headers = {"X-Auth-Token": API_KEY}
        resp = requests.get(team_url, headers=headers)

        if resp.status_code == 200:
            data = resp.json()
            teams = data.get("teams", [])

            for team in teams:
                if team.get("shortName"):
                    team_name = team.get("shortName")
                    area = team.get("area", {})
                    country_name = area.get("name")
                    # print(country_name)

                    if country_name:
                        if country_name in countryteams:
                            countryteams[country_name].append(team_name)
                        else:
                            countryteams[country_name] = [team_name]
        else:
            print(f"Failed to fetch teams for competition {comp_id}. Status code: {resp.status_code}")

    # pprint.pprint(countryteams)
    return countryteams


def set_up_database(db_name):
    """
    Sets up a connection to a SQLite database and enables foreign key support.
    
    Args:
        db_name (str): The name of the SQLite database file to create or connect to.
    
    Returns:
        tuple: A tuple containing the cursor and connection objects for the database.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    return cur, conn


def set_up_countryid_table(data, cur, conn):
    """
    Creates and populates a 'Countries' table in the database with data from a dictionary.
    
    Args:
        data (dict): A dictionary where keys are country names.
        cur : Cursor object to execute SQLite commands.
        conn : Connection object to commit changes to the database.
    """
    cur.execute("PRAGMA foreign_keys = OFF;")
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("CREATE TABLE IF NOT EXISTS Countries (id INTEGER PRIMARY KEY, country)")

    for country in data.keys():
        # print(country)
        cur.execute("INSERT OR IGNORE INTO Countries (country) VALUES (?)", (country,))

    conn.commit()    

def set_up_teams_table(data, cur, conn):
    """
    Creates and populates a 'Teams' table in the database with data from a dictionary.
    
    Args:
        data (dict): A dictionary where keys are country names and values are lists of team names.
        cur: Cursor object to execute SQLite commands.
        conn: Connection object to commit changes to the database.
    """

    cur.execute(
        """CREATE TABLE IF NOT EXISTS Teams (id INTEGER PRIMARY KEY, 
            name TEXT UNIQUE, 
            country_id INTEGER,
            FOREIGN KEY (country_id) REFERENCES Countries (id))"""
    )
    
    # print(data)
    for country, teams in data.items():

        cur.execute("SELECT id FROM Countries WHERE country = ?", (country,))
        country_id = cur.fetchone()
        
        if country_id:
            country_id = country_id[0]

            for team_name in teams:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO Teams (name, country_id) 
                    VALUES (?, ?)
                    """,
                    (team_name, country_id)
                )

    conn.commit()

def num_teams_country(cur, conn):

    query = """
    SELECT Countries.country, COUNT(Teams.id) AS team_count
    FROM Teams
    JOIN Countries ON Teams.country_id = Countries.id
    GROUP BY Countries.country
    """
    cur.execute(query)
    data = cur.fetchall()

    conn.close()

    countries = [row[0] for row in data]
    team_counts = [row[1] for row in data]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(countries, team_counts, color="skyblue")
    plt.xlabel("Country", fontsize=12)
    plt.ylabel("Number of Teams", fontsize=12)
    plt.title("Number of Teams per Country", fontsize=14)
    plt.xticks(rotation=45, ha="right")

    for bar, count in zip(bars, team_counts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, str(count), ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.show()


def main():
    comp_ids = get_comp_id()
    # print(comp_ids)
    data = get_comp_teams(comp_ids)

    cur, conn = set_up_database("206_final.db")
    set_up_countryid_table(data, cur, conn)
    set_up_teams_table(data, cur, conn)
    num_teams_country(cur, conn)
    conn.close()

if __name__ == "__main__":
    main()