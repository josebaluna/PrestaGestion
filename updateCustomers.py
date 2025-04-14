import requests
from conectionSQLite import conn, cur
import logging as log
from datetime import date

outfile = "./log/upd_customers_" + str(date.today()) +".log"
log.basicConfig(filename=outfile, format="'%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s'", level=log.DEBUG, filemode="a")
logger = log.getLogger()

api_url = 'http://s448296819.mialojamiento.es/'
resource = 'customers'
api_key = 'Z9LUNFASYWMAISBXDYEUIWTX2RJYG2S4'
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

if 'data' in locals():
    cur.executemany("INSERT INTO customers "
                    "VALUES(:id, :lastname, :firstname, :email, :company, :note, :id_shop, :date_upd) "
                    "ON CONFLICT(id) DO UPDATE SET email = :email, note = :note, date_upd = :date_upd",
                    data[resource]
                    )
    conn.commit()
    conn.close()

    print("Usuarios actualizados:", len(data[resource]))
