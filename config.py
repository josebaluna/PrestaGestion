import tkinter as tk
from tkinter import simpledialog
import configparser
class Configuracion:
    def __init__(self, root):
        self.root = root
        self.configuracion = configparser.ConfigParser()
        self.configuracion.read('config.ini')

    def obtener_parametro(self, seccion, clave, fallback=""):
        try:
            return self.configuracion.get(seccion, clave)
        except configparser.NoOptionError:
            return fallback

    def obtener_sonido_activado(self):
        return self.obtener_parametro("POS", "sonido_activado", fallback="True").lower() == "true"

    def mostrar_ventana_parametros(self):
        # Crear una nueva ventana para ingresar los parámetros de configuración
        self.ventana_parametros = tk.Toplevel(self.root)
        self.ventana_parametros.title("Parámetros")

        # Leer la configuración actual del archivo config.ini
        configuracion = configparser.ConfigParser()
        configuracion.read('config.ini')

        # Obtener los parámetros de la sección "Api"
        api_url = configuracion.get("Api", "api_url", fallback="")
        api_key = configuracion.get("Api", "api_key", fallback="")
        # Obtener los parámetros de la sección "Shop"
        id_lang = configuracion.get("Shop", "id_lang", fallback="")
        id_carrier = configuracion.get("Shop", "id_carrier", fallback="")
        id_shop = configuracion.get("Shop", "id_shop", fallback="")
        id_currency = configuracion.get("Shop", "id_currency", fallback="")
        id_customer_default = configuracion.get("Shop", "id_customer_default", fallback="")
        sonido_activado = configuracion.getboolean("POS", "sonido_activado", fallback=True)

        # Crear los campos de entrada para los parámetros
        tk.Label(self.ventana_parametros, text="API Url:").grid(row=0, column=0)
        self.entry_api_url = tk.Entry(self.ventana_parametros)
        self.entry_api_url.insert(0, api_url)
        self.entry_api_url.grid(row=0, column=1)

        tk.Label(self.ventana_parametros, text="API Key:").grid(row=1, column=0)
        self.entry_api_key = tk.Entry(self.ventana_parametros)
        self.entry_api_key.insert(0, api_key)
        self.entry_api_key.grid(row=1, column=1)

        tk.Label(self.ventana_parametros, text="Id Lang:").grid(row=2, column=0)
        self.entry_id_lang = tk.Entry(self.ventana_parametros)
        self.entry_id_lang.insert(0, id_lang)
        self.entry_id_lang.grid(row=2, column=1)

        tk.Label(self.ventana_parametros, text="Id Carrier:").grid(row=3, column=0)
        self.entry_id_carrier = tk.Entry(self.ventana_parametros)
        self.entry_id_carrier.insert(0, id_carrier)
        self.entry_id_carrier.grid(row=3, column=1)

        tk.Label(self.ventana_parametros, text="Id Shop:").grid(row=4, column=0)
        self.entry_id_shop = tk.Entry(self.ventana_parametros)
        self.entry_id_shop.insert(0, id_shop)
        self.entry_id_shop.grid(row=4, column=1)

        tk.Label(self.ventana_parametros, text="Id Currency:").grid(row=5, column=0)
        self.entry_id_currency = tk.Entry(self.ventana_parametros)
        self.entry_id_currency.insert(0, id_currency)
        self.entry_id_currency.grid(row=5, column=1)

        tk.Label(self.ventana_parametros, text="Id Customer Default:").grid(row=6, column=0)
        self.entry_id_customer_default = tk.Entry(self.ventana_parametros)
        self.entry_id_customer_default.insert(0, id_customer_default)
        self.entry_id_customer_default.grid(row=6, column=1)

        # Crear checkbutton para activar/desactivar sonido
        self.sonido_activado_var = tk.BooleanVar(value=sonido_activado)
        self.entry_sonido_activado = tk.Checkbutton(self.ventana_parametros, text="Reproducir sonido", variable=self.sonido_activado_var)
        self.entry_sonido_activado.grid(row=7, column=0, columnspan=2, padx=10, pady=10)


        # Crear botones para guardar y cancelar
        tk.Button(self.ventana_parametros, text="Guardar", command=self.guardar_parametros).grid(row=10, column=0, pady=10)
        tk.Button(self.ventana_parametros, text="Cancelar", command=self.ventana_parametros.destroy).grid(row=10, column=1, pady=10)


    def borrar_texto_entrada(self, event, entry):
        if entry.get() == entry.get().split("Ejemplo: ")[-1]:
            entry.delete(0, tk.END)

    def mostrar_texto_entrada(self, event, entry):
        if not entry.get():
            entry.insert(0, "Ejemplo: " + entry.get().split("Ejemplo: ")[-1])

    def guardar_parametros(self):
        # Obtener los valores de los campos de entrada
        nueva_api_url = self.entry_api_url.get()
        nueva_api_key = self.entry_api_key.get()
        nuevo_id_lang = self.entry_id_lang.get()
        nuevo_id_carrier = self.entry_id_carrier.get()
        nuevo_id_shop = self.entry_id_shop.get()
        nuevo_id_currency = self.entry_id_currency.get()
        nuevo_id_customer_default = self.entry_id_customer_default.get()
        nuevo_valor_sonido = self.sonido_activado_var.get()

        # Guardar los parámetros en el archivo de configuración
        self.guardar_configuracion("Api", "api_url", nueva_api_url)
        self.guardar_configuracion("Api", "api_key", nueva_api_key)
        self.guardar_configuracion("Shop", "id_lang", nuevo_id_lang)
        self.guardar_configuracion("Shop", "id_carrier", nuevo_id_carrier)
        self.guardar_configuracion("Shop", "id_shop", nuevo_id_shop)
        self.guardar_configuracion("Shop", "id_currency", nuevo_id_currency)
        self.guardar_configuracion("Shop", "id_customer_default", nuevo_id_customer_default)
        self.guardar_configuracion("POS", "sonido_activado", str(nuevo_valor_sonido))

        # Cerrar la ventana de parámetros
        self.ventana_parametros.destroy()

    def guardar_configuracion(self, seccion, clave, valor):
        # Leer la configuración actual
        configuracion = configparser.ConfigParser()
        configuracion.read('config.ini')

        # Actualizar o agregar la nueva configuración
        if seccion not in configuracion:
            configuracion.add_section(seccion)
        configuracion.set(seccion, clave, valor)

        # Guardar la configuración en el archivo config.ini
        with open('config.ini', 'w') as archivo_config:
            configuracion.write(archivo_config)