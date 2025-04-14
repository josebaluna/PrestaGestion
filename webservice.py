import requests
import xml.etree.ElementTree as ET
import configparser

class WebService:
    def __init__(self):
        # Obtener el objeto config
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        # Connection parameters to the webservice
        self.api_url = self.config['Api']['api_url']
        self.api_key = self.config['Api']['api_key']
        self.schema_param = 'schema=blank'
        self.id_shop = self.config['Shop']['id_shop']
        self.id_lang = self.config['Shop']['id_lang']
        self.id_currency = self.config['Shop']['id_currency']
        self.id_carrier = self.config['Shop']['id_carrier']

    def obtener_schema_vacio(self, resource):
        # Build the URL for the GET request to the empty schema
        url = f'{self.api_url}/{resource}?{self.schema_param}&ws_key={self.api_key}'
        # Send the GET request to retrieve the empty schema
        response = requests.get(url)
        if response.status_code == 200:
            return ET.fromstring(response.text)
        else:
            print(f"Request error: {response.status_code}")
            return None

    def obtener_id_address_delivery(self, cliente_id):
        # URL to create a new product
        url = f'{self.api_url}/addresses/?ws_key={self.api_key}'
        response = requests.post(url, data=modified_xml, headers={'Content-Type': 'application/xml'})
        print("Request:", response.content)

    def crear_carrito(self, cliente_id, productos):
        # Load the XML content from the response
        root = self.obtener_schema_vacio('carts')
        if not root:
            return False

        # Datos para añadir
        datos = {
            "id_address_delivery": self.obtener_id_address_delivery(cliente_id),
            "id_currency": self.id_currency,
            "id_customer": str(cliente_id),
            "id_shop": self.id_shop,
            "id_lang": self.id_lang,
        }

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
        create_url = f'{self.api_url}/carts?ws_key={self.api_key}'
        response = requests.post(create_url, data=modified_xml, headers={'Content-Type': 'application/xml'})
        print("Request:", response.content)

        # Check if the request was successful
        if response.status_code == 201:
            # Display success message
            print("The new cart has been created successfully.")
            return self.extraer_id(response.content)
        else:
            # Display error message if the request failed
            print(f"Error creating the cart: {response.status_code}")

    def extraer_id(self, xml_content):
        root = ET.fromstring(xml_content)
        id_element = root.find(".//id")
        if id_element is not None:
            print(id_element.text)
            return id_element.text
        return None

    def crear_pedido(self, id_cart, cliente_id, total_paid):
        root = self.obtener_schema_vacio('orders')
        if not root:
            return None

        # Datos para añadir
        datos = {
            "id_address_delivery": "8",
            "id_address_invoice": "8",
            "id_cart": str(id_cart),
            "id_currency": self.id_currency,
            "id_shop": self.id_shop,
            "id_lang": self.id_lang,
            "id_customer": str(cliente_id),
            "id_carrier": self.id_carrier,
            "module": "ps_checkpayment",
            "payment": "Payment by check",
            "total_paid": str(total_paid),
            "total_paid_real": str(total_paid),
            "total_products": str(total_paid),
            "total_products_wt": str(total_paid),
            "conversion_rate": "0"
        }
        print(datos)
        # Actualizar los campos existentes o añadir nuevos campos
        for clave, valor in datos.items():
            elemento = root.find(f".//{clave}")
            if elemento is not None:
                elemento.text = valor
            else:
                elemento = ET.SubElement(root, clave)
                elemento.text = valor

        try:
            # Convert the XML tree to a string and encode to UTF-8
            modified_xml = ET.tostring(root, encoding="unicode").encode('utf-8')
            # Display the modified XML content
            print(modified_xml)
        except ET.ParseError as e:
            print(f"XML parse error: {e}")
            return None

        # URL to create a new order
        create_url = f'{self.api_url}/orders?ws_key={self.api_key}'
        response = requests.post(create_url, data=modified_xml, headers={'Content-Type': 'application/xml'})
        print("Request:", response.content)

        if response.status_code == 201:
            print("The new order has been created successfully.")
            return self.extraer_id(response.content)
        else:
            print(f"Error creating the order: {response.status_code}")
            print("Request error:", response.content)
            return None