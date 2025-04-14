import requests
from urllib.request import urlopen
import json

try:
    from urllib import parse
except Exception as e:
    import urllib as parse


api_url = ''
api_key = ''
format = 'JSON'

# Resource to retrieve the empty schema
resource = 'orders'
schema_param = 'schema=blank'

#payload = {'ws_key':'Z9LUNFASYWMAISBXDYEUIWTX2RJYG2S4',
#      'output_format':'JSON'}
data = {'reference': 'TEST'}

#url = 'http://s448296819.mialojamiento.es/api/orders/1&{}'.format(parse.urlencode(payload))
url = f'{api_url}/{resource}?ws_key={api_key}&output_format={format}'

r = requests.put(url,data=data)
print(r.url)

# store the response of URL
response = urlopen(url)
# storing the JSON response
# from url in data
data_json = json.loads(response.read())

# print the json response
print(data_json)

for i in data_json["orders"]:
    url = f"{api_url}/{resource}/{i['id']}?ws_key={api_key}&output_format={format}"
    r = requests.put(url, data=data)
    response = urlopen(url)
    data_json = json.loads(response.read())
    print(data_json)



