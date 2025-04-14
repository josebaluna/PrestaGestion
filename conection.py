import requests

# Connection parameters to the webservice
api_url = ''
api_key = ''
display = 'full'
# Resource to retrieve the empty schema
resource = 'orders'
schema_param = 'schema=blank'

# Build the URL for the GET request to the empty schema
url = f'{api_url}/{resource}?{schema_param}&ws_key={api_key}'

# Send the GET request to retrieve the empty schema
response = requests.get(url, params={"ws_key": api_key, "output_format": "JSON", "display": display})

# Check if the request was successful
if response.status_code == 200:
    # Load the JOSN content from the response
    data = response.json()
    print(data)
