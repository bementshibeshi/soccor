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
        
        # print(comp_ids)
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
            continue
    
        nested_dict = pprint.pprint(comp_teams)
    return comp_teams

def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_teams_table(data, cur, conn):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Teams (id INTEGER PRIMARY KEY, name TEXT UNIQUE)"
    )
    
    # print(data)
    count = 0
    for team in data.items():
        # print(team)

        for name in team[1]:
            team_name = name
            # print(team_name)
            count += 1
            if team_name:
                cur.execute(
                    "INSERT OR IGNORE INTO Teams (id, name) VALUES (?, ?)", (count, team_name)
                )
    
    conn.commit()


def main():
    comp_ids = get_comp_id()
    # print(comp_ids)
    data = get_comp_teams(comp_ids)

    cur, conn = set_up_database("206_final.db")
    set_up_teams_table(data, cur, conn)
    create_teams_table(data, cur, conn)
    conn.close()
    # FEEL FREE TO USE THIS SPACE TO TEST OUT YOUR FUNCTIONS


if __name__ == "__main__":
    main()