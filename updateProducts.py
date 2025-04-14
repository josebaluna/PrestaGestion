import requests
from conectionSQLite import conn, cur
from bs4 import BeautifulSoup
import logging as log
from datetime import date
import configparser

outfile = "./log/upd_products_" + str(date.today()) +".log"
log.basicConfig(filename=outfile, format="'%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s'", level=log.DEBUG, filemode="a")
logger = log.getLogger()

# Obtener el objeto config
config = configparser.ConfigParser()
# leer el archivo
config.read(filenames="config.ini")

# Connection parameters to the webservice
api_url = config['Api']['api_url'] # 'http://s448296819.mialojamiento.es/api'
api_key = config['Api']['api_key'] #'Z9LUNFASYWMAISBXDYEUIWTX2RJYG2S4'
resource = 'products'
display = 'full' #'[id,ean13,name,description,quantity,price,id_category_default,manufacturer_name,link_rewrite,date_upd]'  # 'full'

try:
    response = requests.get(f"{api_url}api/{resource}", params={"ws_key": api_key, "output_format": "JSON", "display": display})
except requests.RequestException as ex:
    print(f"Request error: {ex}")
    logger.setLevel(log.CRITICAL)
    log.critical(ex)
    logger.setLevel(log.WARNING)
    log.warning(ex)
else:
    if response.status_code == requests.codes.ok:
        data = response.json()
        # print(data)

def limpiar_descripcion(descripcion_html):
    # Utilizar BeautifulSoup para eliminar etiquetas HTML
    soup = BeautifulSoup(descripcion_html, "html.parser")
    descripcion_limpia = soup.get_text(separator=" ")

    return descripcion_limpia

if 'data' in locals():
    # Limpiar la descripción HTML
    for product in data[resource]:
        product['description'] = limpiar_descripcion(product['description'])
        product['id_default_image'] = api_url + "img/p/" + str(product['id']) + "/" + str(product['id_default_image']) + "-home_default.jpg"

    cur.executemany("INSERT INTO products "
                    "VALUES(:id, :ean13, :name, :description, :id_default_image, :quantity, :price, :id_category_default, :manufacturer_name, :link_rewrite, :date_upd) "
                    "ON CONFLICT(id) DO UPDATE SET price = :price, stock = :quantity, date_upd = :date_upd, description = :description, image = :id_default_image, ean = :ean13",
                    data[resource]
                    )
    conn.commit()
    conn.close()

    print("Productos actualizados:", len(data[resource]))
