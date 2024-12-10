# import unittest
# import sqlite3
# import json
# import os
# import requests
# import pprint

# def get_games_cancelled():

#     API_KEY = "acf0777e33msha5e9de947da5ee5p1797f8jsnbb4a8ec0bba6"
#     url = "https://api.soccerfootball.info/v1/matches/day/basic/?d=DATE"
#     headers = {"X-Auth-Token": API_KEY}
    
#     headers = {
#         "x-rapidapi-key": API_KEY,
#         "x-rapidapi-host": "soccer-football-info.p.rapidapi.com"
#     }

#     response = requests.get(url, headers=headers)

#     print(response.json())