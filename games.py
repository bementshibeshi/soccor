import sqlite3
import os
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

def set_up_database(db_name):

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(os.path.join(path, db_name))
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    return cur, conn


def get_canceled_games(cur):

    start_date = datetime(2020, 3, 1)
    end_date = datetime(2020, 6, 1)

    date_list = []
    current_date = start_date

    while current_date <= end_date:
        date_list.append(current_date.strftime("%Y%m%d"))
        current_date += timedelta(days=1)
    # print(date_list)

    canceled_games = []

    for date in date_list:
        # print(date)
    
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-matches-by-date"
        querystring = {"date":{date}}
        headers = {
            "x-rapidapi-key": "3088ad0d02msh18679a1f27d9af9p12a499jsna45b809e908b",
            "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
        }
    
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()
            # print(data)

            cur.execute("SELECT name FROM Teams")
            team_name = cur.fetchall()
            teamlist = [name[0] for name in team_name]

            matches = data.get('response', {}).get('matches', [])
            
            allteams = []

            for match in matches:
                match_date = date
                # print(match_date)
                hometeam = match['home']['name']
                awayteam = match['away']['name']
                is_canceled = match['status']['cancelled']
                # print(is_canceled)

                if not matches:
                    print(f"No matches found for date: {date}")
                    continue  


                if hometeam not in allteams:
                    allteams.append(hometeam) 

                if awayteam not in allteams:
                    allteams.append(awayteam)

                if is_canceled:

                    for team in allteams:
                        if team in teamlist:
                            cur.execute('''
                                SELECT Countries.id
                                FROM Teams
                                JOIN Countries ON Teams.country_id = Countries.id
                                WHERE Teams.name = ?
                            ''', (team,))
                            country_id = cur.fetchone()

                            if country_id:
                                canceled_games.append({
                                    "date": match_date,
                                    "team": team,
                                    "country_id": country_id[0]
                                })

        else:
            print(f"Failed to fetch data. Status code: {response.status_code}, Reason: {response.reason}")
    print(f"Total canceled games found: {len(canceled_games)}")
    # print(canceled_games)
    return canceled_games

def insert_to_db(canceled_data, cur, conn):

    cur.execute("""DROP TABLE IF EXISTS Games_Canceled""")
    
    cur.execute('''
    CREATE TABLE Games_Canceled (
        date TEXT,
        team TEXT,
        country_id INTEGER,
        UNIQUE (date, team, country_id)
    )
    ''')

    for game in canceled_data:
        # print(game)
        cur.execute('''
            INSERT OR IGNORE INTO Games_Canceled (date, team, country_id)
            VALUES (?, ?, ?)
        ''', (game['date'], game['team'], game['country_id']))

    conn.commit()

def canceled_games_country(cur, conn):

    # Query to get the number of canceled games per country
    query = '''
    SELECT Countries.country AS country, COUNT(Games_Canceled.country_id) AS canceled_count
    FROM Games_Canceled
    JOIN Countries ON Games_Canceled.country_id = Countries.id
    GROUP BY Countries.country
    ORDER BY canceled_count DESC
    '''
    cur.execute(query)
    data = cur.fetchall()

    conn.close()

    df = pd.DataFrame(data, columns=['Country', 'Canceled Games'])

    plt.figure(figsize=(12, 6))
    plt.bar(df['Country'], df['Canceled Games'], color='skyblue')

    plt.title('Number of Canceled Games per Country', fontsize=16)
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Canceled Games', fontsize=12)
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

import pandas as pd
import matplotlib.pyplot as plt


def canceled_games_team(cur, conn):
    
    query = '''
    SELECT Teams.name AS team, COUNT(Games_Canceled.team) AS canceled_count
    FROM Games_Canceled
    JOIN Teams ON Games_Canceled.team = Teams.name
    GROUP BY Teams.name
    ORDER BY canceled_count DESC
    '''
    cur.execute(query)
    data = cur.fetchall()

    conn.close()

    # Create a DataFrame
    df = pd.DataFrame(data, columns=['Teams', 'Canceled Games'])

    # Select the top 10 teams
    top_teams = df.head(10)

    # Plot the top 10 teams
    plt.figure(figsize=(12, 6))
    plt.bar(top_teams['Teams'], top_teams['Canceled Games'], color='pink')

    plt.title('Top 10 Teams with the Most Canceled Games', fontsize=16)
    plt.xlabel('Teams', fontsize=12)
    plt.ylabel('Canceled Games', fontsize=12)
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()



def main():
    cur, conn = set_up_database("206_final.db")
    # canceled_data = get_canceled_games(cur) do not run api again unless you need the data
    # insert_to_db(canceled_data, cur, conn)
    # canceled_games_country(cur, conn)
    canceled_games_team(cur, conn)
    conn.close()


if __name__ == "__main__":
    main()
