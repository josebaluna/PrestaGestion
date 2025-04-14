import sqlite3
import sys
import configparser

class Database:
    def __init__(self):
        try:
            self.config = self.leer_configuracion()
            self.conexion = sqlite3.connect(self.config['Default']['database'])
            self.conexion.row_factory = sqlite3.Row
            self.cursor = self.conexion.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to BD Platform: {e}")
            sys.exit(1)

    def leer_configuracion(self):
        config = configparser.ConfigParser()
        config.read(filenames="config.ini")
        return config

    def obtener_productos(self):
        query = "SELECT * FROM products"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def obtener_clientes(self):
        query = "SELECT * FROM customers"
        self.cursor.execute(query)
        return self.cursor.fetchall()
        self.db.guardar_ticket(cliente_id, pago, total, productos_json, fecha)

    def guardar_ticket(self, cliente_id, pago, productos, total, fecha):
        query = """INSERT INTO tickets (id_customer, payment, products, total_paid, date_add) 
                   VALUES (?, ?, ?, ?, ?)"""
        self.cursor.execute(query, (cliente_id, pago, productos, total, fecha))
        self.conexion.commit()
        return self.cursor.lastrowid  # Devolver el ID del ticket recién insertado

    def guardar_order(self, id_ticket, id_cart, id_order):
        query = """UPDATE tickets 
                   SET id_cart = ?, id_order = ?
                   WHERE id = ?"""
        self.cursor.execute(query, (id_cart, id_order, id_ticket))
        self.conexion.commit()

    def obtener_imagen(self):
        pass

    def cerrar(self):
        self.conexion.close().close()