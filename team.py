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
    comp_teams = {}  # Dictionary to store teams by competition ID

    for comp_id in comp_ids:  # Limit to the first 3 competition IDs for testing
        team_url = f"http://api.football-data.org/v4/competitions/{comp_id}/teams"
        headers = {"X-Auth-Token": API_KEY}
        resp = requests.get(team_url, headers=headers)

        if resp.status_code == 200:
            data = resp.json()  # Parse JSON response
            teams = data.get("teams", [])  # Get the list of teams
            team_names = [team.get("name") for team in teams if team.get("name")]  # Extract team names
            comp_teams[comp_id] = team_names  # Map the competition ID to its teams
        else:
            print(f"Failed to fetch teams for competition {comp_id}. Status code: {resp.status_code}")
            comp_teams[comp_id] = []  # Assign an empty list for failed requests
    
    return comp_teams  # Return the nested dictionary

comp_ids = get_comp_id()
nested_dict = get_comp_teams(comp_ids)

# Print the nested dictionary in a readable format
import pprint
pprint.pprint(nested_dict)

