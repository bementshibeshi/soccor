import requests

def get_games_cancelled():
    API_KEY = "ddcbb4fe7a924d672ecd0dcd73aee729"  # Use your API key here
    team_url = "https://api.soccersapi.com/v2.2/fixtures/?user={{bemnet}}&token={{ddcbb4fe7a924d672ecd0dcd73aee729}}"
    headers = {"X-Auth-Token": API_KEY}
    
    # Make the request with the correct headers
    resp = requests.get(team_url, headers=headers)
    
    # Check if the request was successful
    if resp.status_code == 200:
        data = resp.json()
        print(data)  # Optionally print the data or process it as needed
    else:
        print(f"Failed to fetch data. Status code: {resp.status_code}, Reason: {resp.reason}")

# Call the function
get_games_cancelled()