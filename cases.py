import requests
import json
import pandas as pd

# POST to API
payload = {'code': 'ALL'}
URL = 'https://api.statworx.com/covid'
response = requests.post(url=URL, data=json.dumps(payload))

# Convert to data frame
df = pd.DataFrame.from_dict(json.loads(response.text))
print(len(response.json().get("cases_cum")))