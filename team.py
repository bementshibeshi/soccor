import unittest
import sqlite3
import json
import os
import requests
import pprint


def get_comp_id():
    API_KEY = "0cd173cf1b864ce092037aec02a7fdcb"
    team_url = "http://api.football-data.org/v4/competitions/"
    headers = {"X-Auth-Token": API_KEY}
    
    resp = requests.get(team_url, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        
        competitions = data.get("competitions", [])
        
        comp_ids = [comp["id"] for comp in competitions if "id" in comp]
        
        return comp_ids
    else:
        print(f"Error: {resp.status_code} - {resp.reason}")
        return None


def get_comp_teams(comp_ids):
    API_KEY = "0cd173cf1b864ce092037aec02a7fdcb"
    comp_teams = {}  

    for comp_id in comp_ids:
        team_url = f"http://api.football-data.org/v4/competitions/{comp_id}/teams"
        headers = {"X-Auth-Token": API_KEY}
        resp = requests.get(team_url, headers=headers)

        if resp.status_code == 200:
            data = resp.json()  
            teams = data.get("teams", [])  
            team_names = [team.get("name") for team in teams if team.get("name")] 
            comp_teams[comp_id] = team_names 
        else:
            print(f"Failed to fetch teams for competition {comp_id}. Status code: {resp.status_code}")
            comp_teams[comp_id] = [] 
    
    return comp_teams 

# Example usage

comp_ids = get_comp_id()
nested_dict = get_comp_teams(comp_ids)

pprint.pprint(nested_dict)

def set_up_database(db_name):
    """
    Sets up a SQLite database connection and cursor.

    Parameters
    -----------------------
    db_name: str
        The name of the SQLite database.

    Returns
    -----------------------
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn