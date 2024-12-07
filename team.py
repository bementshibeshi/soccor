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
    # print(resp)

    comp_ids = []

    #check the if the status is valid 200 means it is okay 
    if resp.status_code == 200:
        #get the data content of the movie
        data = resp.json()
        # print(data)
        if data.get("Response") == "False":
            return None 
        
    for head in data.items():
        # print(head)
        for info in head:
            print(info)
            for list in info.items():
                print(list)


get_comp_id()

