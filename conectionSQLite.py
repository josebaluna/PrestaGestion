import sqlite3
import sys
import configparser

# Obtener el objeto config
config = configparser.ConfigParser()
# leer el archivo
config.read(filenames="config.ini")
# Abrir una conexion
try:
    conn = sqlite3.connect(config['Default']['database'])
except sqlite3.Error as e:
    print(f"Error connecting to BD Platform: {e}")
    sys.exit(1)

# Obtener un cursor
cur = conn.cursor()

# Si no existe creamos la tabla productos
cur.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, ean INTEGER, name TEXT, description TEXT, image TEXT, stock INTEGER, price REAL, id_category INT, manufacturer TEXT, link TEXT, date_upd DATETIME)")
conn.commit()

# Si no existe creamos la tabla usuarios
cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, lastname TEXT, firstname TEXT, email TEXT, company TEXT, note TEXT, id_shop INT, date_upd DATETIME)")
conn.commit()

# Si no existe creamos la tabla tickets
cur.execute("CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY, id_customer INTEGER, payment TEXT, products TEXT, total_paid REAL, id_cart INTEGER, id_order, date_add DATETIME)")
conn.commit()

# Listado de tablas
products = cur.execute("SELECT * FROM products")
customers = cur.execute("SELECT * FROM customers")
conn.commit()

# cerrar la conexion
#conn.close()

