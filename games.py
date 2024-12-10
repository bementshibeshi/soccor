# import sqlite3
# import os
# import requests
# from datetime import datetime, timedelta

# def set_up_database(db_name):

#     path = os.path.dirname(os.path.abspath(__file__))
#     conn = sqlite3.connect(os.path.join(path, db_name))
#     conn.execute("PRAGMA foreign_keys = ON;")
#     cur = conn.cursor()
#     return cur, conn


# def get_canceled_games(cur, conn):

#     start_date = datetime(2020, 5, 1)
#     end_date = datetime(2020, 6, 1)

#     date_list = []
#     current_date = start_date

#     while current_date <= end_date:
#         date_list.append(current_date.strftime("%Y%m%d"))
#         current_date += timedelta(days=1)


#     for date in date_list:
    
#         url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
#         querystring = {"date": {date}}
#         headers = {
#             "x-rapidapi-key": "acf0777e33msha5e9de947da5ee5p1797f8jsnbb4a8ec0bba6",
#             "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
#         }

#         try:
#             response = requests.get(url, headers=headers, params=querystring)
#             data = response.json()
#         except requests.RequestException as e:
#             print(f"Error fetching data from API: {e}")
#             return
#         except ValueError:
#             print("Error parsing JSON response.")
#             return

#         cur.execute("SELECT name FROM Teams")
#         team_name = cur.fetchall()
#         teamlist = [name[0] for name in team_name]

#         matches = data.get('response', {}).get('matches', [])
#         all_teams = set()
#         canceled_games = []
#         # matched_teams = []

#         for match in matches:
#             match_date = current_date.strftime("%Y%m%d")
#             hometeam = match['home']['name']
#             awayteam = match['away']['name']
#             is_canceled = match['status']['cancelled']

#             all_teams.add(hometeam)
#             all_teams.add(awayteam)

#             for team in teamlist:

#                 if is_canceled and team in all_teams:

#                     canceled_games.append({
#                         "date": match_date,
#                         "team": team
#                     })

#         # print(canceled_games)



# def main():

#     cur, conn = set_up_database("206_final.db")
#     get_canceled_games(cur, conn)
#     conn.close()


# if __name__ == "__main__":
#     main()
