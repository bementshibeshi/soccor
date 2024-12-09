import requests
import json
import pandas as pd

# POST to API
payload = {'code': 'ALL'}
URL = 'https://api.statworx.com/covid'
response = requests.post(url=URL, data=json.dumps(payload))

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Extract the relevant information: country and total cases
    country = data['country']
    total_cases = data['cases']

    # Create a DataFrame with only country and total cases
    df = pd.DataFrame({'Country': [country], 'Total Cases': [total_cases]})

    print(df)
else:
    print(f"Failed to fetch data. Status code: {response.status_code}, Reason: {response.reason}")