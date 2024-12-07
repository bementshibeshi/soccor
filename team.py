import unittest
import sqlite3
import json
import os
import requests

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
    # print(comp_ids)

    for id in comp_ids[:3]:
        # print(id)
        team_url = f"http://api.football-data.org/v4/competitions/{id}/teams"
        headers = {"X-Auth-Token": API_KEY}  
        resp = requests.get(team_url, headers=headers)

        if resp.status_code == 200:
            data = resp.json()

        print(data[0])


get_comp_id()
get_comp_teams(get_comp_id())


