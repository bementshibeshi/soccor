import unittest
import sqlite3
import json
import os
import requests
import pprint

API_KEY = "32fb007eb213dce09cf03a5cb3edfc00"


def get_country_names():
    """
    Fetches a list of country names where football teams are available.

    Returns:
        list: A list of country names.
    """
    url = "https://v3.football.api-sports.io/teams/countries"

    headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.request("GET", url, headers=headers)

    #print(response)

    if response.status_code == 200:
        data = response.json()

        country_name_list = []

        response_info = data.get("response", [])

        for item in response_info:
            country_name_list.append(item["name"])

    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return None

    print(country_name_list)
    return country_name_list


def teams_to_countries(country_names):
    """
    Fetches teams for each country and maps them.

    Args:
        country_names (list): A list of country names.

    Returns:
        dict: A dictionary mapping country names to lists of team names.
    """
    teams = {} 
    for country in country_names:
        url = f"https://v3.football.api-sports.io/teams?country={country}"
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            response_info = data.get("response", [])

            for item in response_info:
                country_name = item["team"]["country"]  
                team_name = item["team"]["name"] 

                if country_name in teams:
                    teams[country_name].append(team_name)  
                else:
                    teams[country_name] = [team_name]
        else:
            print(f"Failed to fetch data for {country}. Status code: {response.status_code}")

    # pprint.pprint(teams)
    return teams

def set_up_database(db_name):
    """
    Sets up a SQLite database connection.

    Args:
        db_name (str): Name of the database file.

    Returns:
        cur: Cursor object for database operations.
        conn: Connection object for the database.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn


def set_up_countries_table(data, cur, conn):
    """
    Creates and populates the Teams table in the database.

    Args:
        data (dict): A dictionary mapping country names to team names.
        cur: Cursor object for database operations.
        conn: Connection object for the database.
    """
    cur.execute("DROP TABLE IF EXISTS Countries")
    cur.execute("CREATE TABLE IF NOT EXISTS Countries (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    
    for country in data.items():

        countryname = country["name"]
        cur.execute(
            "INSERT OR IGNORE INTO Countries (name) VALUES (?)", (countryname,)
        )
    conn.commit()


def main():

    country_data = get_country_names()

    teams_to_countries(country_data)

    if not country_data:
        print("No country data retrieved. Exiting.")
        return

    # cur, conn = set_up_database("206_final.db")
    # set_up_countries_table(country_data, cur, conn)
    # conn.close()


if __name__ == "__main__":
    main()