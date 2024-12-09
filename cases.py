import requests
import json
import pandas as pd
from datetime import datetime

# POST to API
payload = {'code': 'ALL'}
URL = 'https://api.statworx.com/covid'
response = requests.post(url=URL, data=json.dumps(payload))

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Convert the response data to a DataFrame
    df = pd.DataFrame.from_dict(json.loads(response.text)) 

    # Check if the DataFrame contains the necessary columns
    if 'date' in df.columns:
        # Convert 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'])

        # Extract the year and month for easier filtering
        df['month'] = df['date'].dt.to_period('M')  # This will give 'YYYY-MM' format

        # Now, get the last record for each country per month
        df_last_day_of_month = df.groupby(['month', 'country']).apply(lambda group: group[group['date'] == group['date'].max()]).reset_index(drop=True)

        # Create a column for the last day of the month (this will be the last date from 'date' column)
        df_last_day_of_month['last_day_of_month'] = df_last_day_of_month['date'].dt.strftime('%Y-%m-%d')

        # Drop unnecessary columns
        df_last_day_of_month = df_last_day_of_month[['last_day_of_month', 'country', 'cases']]  # Keep only the last_day_of_month, country, and cases columns

        # Display the result for the last day of each month for every country
        print(df_last_day_of_month)
    else:
        print("The expected 'date' column is not present in the data.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}, Reason: {response.reason}")