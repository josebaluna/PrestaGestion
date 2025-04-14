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
resource = 'carts'
schema_param = 'schema=blank'

# Build the URL for the GET request to the empty schema
url = f'{api_url}/{resource}?{schema_param}&ws_key={api_key}'
print(url)
# Send the GET request to retrieve the empty schema
response = requests.get(url)

"""My first thought would be Using the API to:
1. Create a cart
2. Create a customer
3. Create "addresses"
4. Then finally create the order synchronizing all the tables."""

# Datos para añadir
datos = {
    "id_currency": config['Shop']['id_currency'],
    "id_customer": "3",
    "id_lang": config['Shop']['id_lang'],
}
products = {
    "id_product": ["1","2"],
    "quantity": ["3","1"],
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

    # Obtener el elemento "cart_rows" o crearlo si no existe
    cart_rows = root.find(".//cart_rows")
    if cart_rows is None:
        cart_rows = ET.SubElement(root.find(".//associations"), "cart_rows")

    # Iterar sobre los datos de los productos y agregar cada producto como un nuevo elemento "cart_row"
    for i in range(len(productos["id_product"])):
        cart_row = ET.SubElement(cart_rows, "cart_row")
        for etiqueta, valores in productos.items():
            # Crear y agregar cada etiqueta con su valor correspondiente
            elemento = ET.SubElement(cart_row, etiqueta)
            elemento.text = valores[i]

    # Convert the XML tree to a string
    modified_xml = ET.tostring(root, encoding="unicode")

    # Convert the string to UTF-8 encoding
    modified_xml = modified_xml.encode('utf-8')

    # Display the modified XML content
    print(modified_xml.decode('utf-8'))

    # URL to create a new product
    create_url = f'{api_url}/{resource}?ws_key={api_key}'

    response = requests.post(create_url, data=modified_xml, headers={'Content-Type': 'application/xml'})

    print("Request:", response.content)


    # Check if the request was successful
    if response.status_code == 201:
        # Display success message
        print("The new cart has been created successfully.")
    else:
        # Display error message if the request failed
        print(f"Error creating the cart: {response.status_code}")
else:
    # Display error message if the request failed
    print(f"Request error: {response.status_code}")