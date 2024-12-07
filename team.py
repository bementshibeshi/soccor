import unittest
import sqlite3
import json
import os
import requests

def get_team_data():

    API_KEY = "0cd173cf1b864ce092037aec02a7fdcb"
    team_url = "http://api.football-data.org/v4/teams/"
    headers = {"X-Auth-Token": API_KEY}
    resp = requests.get(team_url, headers=headers) 
    print(resp)

    team_list = []

    #check the if the status is valid 200 means it is okay 
    if resp.status_code == 200:
        #get the data content of the movie
        data = resp.json()
        print(data)
        if data.get("Response") == "False":
            return None 
        return (data,resp.url)

    #if the url is invalid
    return None

get_team_data()

