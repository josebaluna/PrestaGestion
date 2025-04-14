import requests
from conectionSQLite import conn, cur
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
import configparser

# Obtener el objeto config
config = configparser.ConfigParser()
# leer el archivo
config.read(filenames="config.ini")

# Connection parameters to the webservice
api_url = config['Api']['api_url'] # 'http://s448296819.mialojamiento.es/api'
api_key = config['Api']['api_key'] #'Z9LUNFASYWMAISBXDYEUIWTX2RJYG2S4'

# Resource to retrieve the empty schema
resource = 'orders'
schema_param = 'schema=blank'

# Build the URL for the GET request to the empty schema
url = f'{api_url}/{resource}?{schema_param}&ws_key={api_key}'

# Send the GET request to retrieve the empty schema
response = requests.get(url)

"""My first thought would be Using the API to:
1. Create a cart
2. Create a customer
3. Create "addresses"
4. Then finally create the order synchronizing all the tables."""

# Datos para añadir
datos = {
    "id_address_delivery": "7",
    "id_address_invoice": "1",
    "id_cart": "36",
    "id_currency": "1",
    "id_shop": config['Shop']['id_shop'],
    "id_lang": config['Shop']['id_lang'],
    "id_customer": "3",
    "id_carrier": config['Shop']['id_carrier'],
    "module": "ps_checkpayment",
    "payment": "Payment by check",
    "total_paid": "49",
    "total_paid_real": "40",
    "total_products": "40",
    "total_products_wt": "40",
    "conversion_rate": "0"
}

# Check if the request was successful
if response.status_code == 200:
    # Load the XML content from the response
    xml_content = response.text

    # Parse the XML content
    root = ET.fromstring(xml_content)

    # Actualizar los campos existentes o añadir nuevos campos
    for clave, valor in datos.items():
        # Buscar el elemento con la clave actual
        elemento = root.find(f".//{clave}")
        if elemento is not None:
            # Si el elemento existe, actualizar su valor
            elemento.text = valor
        else:
            # Si el elemento no existe, crear un nuevo elemento
            elemento = ET.SubElement(root, clave)
            elemento.text = valor

    # Convert the XML tree to a string
    modified_xml = ET.tostring(root, encoding="unicode")

    # Convert the string to UTF-8 encoding
    modified_xml = modified_xml.encode('utf-8')

    # Display the modified XML content
    print(modified_xml.decode('utf-8'))

    # URL to create a new product
    create_url = f'{api_url}/{resource}?ws_key={api_key}'

    response = requests.post(create_url, data=modified_xml, headers={'Content-Type': 'application/xml'})

    print("Request error:", response.content)


    # Check if the request was successful
    if response.status_code == 201:
        # Display success message
        print("The new order has been created successfully.")
    else:
        # Display error message if the request failed
        print(f"Error creating the order: {response.status_code}")
else:
    # Display error message if the request failed
    print(f"Request error: {response.status_code}")