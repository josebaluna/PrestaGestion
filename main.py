import json
import tkinter as tk
from tkinter import ttk, messagebox
import pygame
from PIL import Image, ImageTk
import requests
from io import BytesIO
from escpos.printer import Usb
import subprocess
import random
from datetime import datetime
from config import Configuracion
from database import Database  # Importa la clase Database
from database_update import actualizar_base_de_datos
from webservice import WebService


class TPVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TPV App")

        # Conectar a la base de datos SQLite3 usando la clase Database
        self.db = Database()

        # Crear una instancia del webservice
        self.webservice = WebService()

        # Crear el menú principal
        self.crear_menu_principal()

        # Actualizar la base de datos al iniciar la aplicación
        self.actualizar_base_de_datos()

        # Inicializar pygame solo si el sonido está activado
        self.sonido_activado = Configuracion.obtener_sonido_activado()
        print(self.sonido_activado)
        if self.sonido_activado:
            pygame.mixer.init()

        # Crear la interfaz de usuario, etc.
        self.crear_interfaz_usuario()

        # Obtener los datos de la BD
        self.productos = self.db.obtener_productos()
        self.clientes = self.db.obtener_clientes()

        # Variables para almacenar los datos
        self.productos_seleccionados = []
        #self.cliente = tk.StringVar()
        self.cliente = tk.IntVar()
        self.total = tk.DoubleVar()

        # Crear widgets
        tk.Label(root, text="Cliente:").grid(row=0, column=0)
        # self.entry_cliente = tk.Entry(root, textvariable=self.cliente)
        self.combo_cliente = ttk.Combobox(root, values=[cliente["id"] for cliente in self.clientes], textvariable=self.cliente)
        self.combo_cliente.grid(row=0, column=1)

        # Campo de entrada para el EAN
        tk.Label(root, text="EAN:").grid(row=1, column=0)
        self.entry_ean = tk.Entry(root)
        self.entry_ean.grid(row=1, column=1)

        # Establecer el foco en el campo de entrada del EAN
        self.entry_ean.focus_set()

        # Botón de búsqueda por EAN
        btn_buscar_ean = tk.Button(root, text="Buscar", command=self.buscar_por_ean)
        btn_buscar_ean.grid(row=1, column=2)

        tk.Label(root, text="Producto:").grid(row=2, column=0)
        self.combo_producto = ttk.Combobox(root, values=[producto["name"] for producto in self.productos])
        self.combo_producto.grid(row=2, column=1)

        # Crear la etiqueta para mostrar la imagen del producto seleccionado
        self.label_imagen = tk.Label(root)
        self.label_imagen.grid(row=0, column=4, rowspan=6, padx=10, pady=10)
        # Etiqueta para mostrar nombre del producto seleccionado
        self.label_nombre = tk.Label(root, text="", wraplength=300)
        self.label_nombre.grid(row=6, column=4, padx=0, pady=0)
        # Etiqueta para mostrar precio del producto seleccionado
        self.label_precio = tk.Label(root, text="", wraplength=300)
        self.label_precio.grid(row=6, column=5, padx=10, pady=10)
        # Etiqueta para mostrar la descripción del producto seleccionado
        #self.label_descripcion = tk.Label(root, text="", wraplength=300)
        #self.label_descripcion.grid(row=6, column=4, rowspan=3, padx=10, pady=10)

        self.combo_producto.bind("<<ComboboxSelected>>", self.mostrar_info_producto)

        tk.Label(root, text="Cantidad:").grid(row=3, column=0)
        self.entry_cantidad = tk.Entry(root)
        self.entry_cantidad.grid(row=3, column=1)

        # Crear Spinbox para la cantidad
        self.entry_cantidad = tk.Spinbox(root, from_=1, to=100)
        self.entry_cantidad.grid(row=3, column=1)

        tk.Button(root, text="Agregar Producto", command=self.agregar_producto).grid(row=4, column=0, columnspan=2)
        tk.Button(root, text="Generar Factura", command=self.generar_factura).grid(row=5, column=0, columnspan=2)
        # Botón para generar factura
        tk.Button(root, text="Generar Factura", command=self.mostrar_datos_factura).grid(row=5, column=3, columnspan=2)

        button = tk.Button(root, text="Print Me", command=self.generar_factura)

        # Botón para imprimir el ticket
        self.boton_imprimir = tk.Button(root, text="Imprimir Ticket", command=self.imprimir_ticket)
        self.boton_imprimir.grid(row=6, column=0, columnspan=2, pady=10)

        # Crear Treeview para mostrar el resumen de los productos en formato de tabla
        self.tree_resumen = ttk.Treeview(root, columns=("ID","Referencia", "Producto", "Cantidad", "Precio", "Importe"), show="headings")
        self.tree_resumen.heading("ID", text="ID")
        self.tree_resumen.column("ID", minwidth=10, width=50, anchor="center")
        self.tree_resumen.heading("Referencia", text="Referencia")
        self.tree_resumen.column("Referencia", minwidth=30, width=150, anchor="center")
        self.tree_resumen.heading("Producto", text="Producto")
        self.tree_resumen.column("Producto", minwidth=100, width=600)
        self.tree_resumen.heading("Cantidad", text="Cantidad")
        self.tree_resumen.column("Cantidad", minwidth=30, width=150, anchor="center")
        self.tree_resumen.heading("Precio", text="Precio")
        self.tree_resumen.column("Precio", minwidth=30, width=150, anchor="center")
        self.tree_resumen.heading("Importe", text="Importe")
        self.tree_resumen.column("Importe", minwidth=30, width=150, anchor="center")
        self.tree_resumen.grid(row=7, column=0, columnspan=7, padx=10, pady=10)

        # Crear la Scrollbar y vincularla al Treeview
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree_resumen.yview)
        self.tree_resumen.configure(yscrollcommand=scrollbar.set)

        # Empaquetar el Treeview y la Scrollbar
        self.tree_resumen.grid(row=7, column=0, columnspan=7, padx=10, pady=10, sticky="nsew")
        scrollbar.grid(row=7, column=7, sticky="ns")

        tk.Label(root, text="Total:").grid(row=8, column=5)
        tk.Label(root, textvariable=self.total).grid(row=8, column=6)

        # Inicializar total en 0
        self.total.set(0)
        self.cliente.set(0)

        """# Crear un Frame para contener los productos en forma de cuadrícula
        self.frame_productos = tk.Frame(root)
        self.frame_productos.grid(row=9, column=0, padx=10, pady=10)

        # Configurar el número de columnas en el Frame
        self.frame_productos.grid_columnconfigure(4, weight=1)  # Expandir la primera columna

        # Luego, puedes llamar a esta función en tu código principal para generar los widgets de los productos:
        self.crear_widgets_productos()"""

    def crear_menu_principal(self):
        # Crear el menú principal
        self.menu_principal = tk.Menu(self.root)
        self.root.config(menu=self.menu_principal)

        # Crear el menú "Configuración"
        self.menu_configuracion = tk.Menu(self.menu_principal, tearoff=False)
        self.menu_principal.add_cascade(label="Configuración", menu=self.menu_configuracion)

        # Crear el menú "Base de datos"
        self.menu_basedatos = tk.Menu(self.menu_principal, tearoff=False)
        self.menu_principal.add_cascade(label="Herramientas", menu=self.menu_basedatos)

        # Crear una instancia de la clase Configuracion
        self.configuracion = Configuracion(self.root)

        # Agregar opción para abrir la ventana de parámetros
        self.menu_configuracion.add_command(label="Ajustar Parámetros", command=self.configuracion.mostrar_ventana_parametros)

        # Agregar una opción para actualizar la base de datos al menú "Base de datos"
        self.menu_basedatos.add_command(label="Actualizar", command=self.actualizar_base_de_datos)

    def actualizar_base_de_datos(self):
        self.mostrar_ventana_actualizacion()

        salida_actualizacion = actualizar_base_de_datos()
        self.estado_actualizacion.config(text=salida_actualizacion)

    def mostrar_ventana_actualizacion(self):
        print("Muestra ventana de actualización")
        self.ventana_actualizacion = tk.Toplevel()
        self.ventana_actualizacion.title("Actualización de la base de datos")

        self.estado_actualizacion = tk.Label(self.ventana_actualizacion, text="Iniciando actualización...")
        self.estado_actualizacion.pack(pady=10)

        # Crear la interfaz de usuario después de mostrar la ventana de actualización
        self.crear_interfaz_usuario()

    def crear_interfaz_usuario(self):
        # Aquí puedes crear el resto de la interfaz de usuario de tu aplicación
        pass

    def mostrar_imagen_producto(self, url_imagen):
        try:
            # Obtener la imagen desde la URL
            response = requests.get(url_imagen, timeout=2.5)
            response.raise_for_status()  # Verificar si hubo algún error al obtener la respuesta

            imagen_bytes = BytesIO(response.content)
            imagen_pil = Image.open(imagen_bytes)

        except Exception as ex:
            print(f"Request error: {ex}")
            # Cargar una imagen por defecto local
            imagen_pil = Image.open("./images/default-small_default.jpg")

        # Redimensionar la imagen si es necesario
        imagen_pil.thumbnail((150, 150))

        # Convertir la imagen a un formato compatible con tkinter
        imagen_tk = ImageTk.PhotoImage(imagen_pil)

        # Mostrar la imagen en un widget Label
        self.label_imagen.config(image=imagen_tk)
        self.label_imagen.image = imagen_tk  # Guardar una referencia para evitar que la imagen sea eliminada por el recolector de basura

        """imagen_widget = tk.Label(self.frame_productos, image=imagen_tk)
        imagen_widget.image = imagen_tk

        return imagen_widget"""

    def mostrar_info_producto(self, event):
        # Obtener el producto seleccionado
        producto_seleccionado = self.combo_producto.get()

        # Buscar el producto seleccionado en la lista de productos
        for producto in self.productos:
            if producto["name"] == producto_seleccionado:
                url_imagen = producto["image"]
                descripcion_producto = producto["description"]
                precio_producto = producto["price"]
                nombre_producto = producto["name"]
                break
        else:
            # Si el producto seleccionado no se encuentra, asignar descripción y URL de imagen vacías
            url_imagen = ""
            descripcion_producto = ""

        # Mostrar la imagen del producto seleccionado
        if url_imagen:
            self.mostrar_imagen_producto(url_imagen)

        # Mostrar la descripción del producto seleccionado
        self.label_nombre.config(text=nombre_producto)

        # Mostrar la descripción del producto seleccionado
        self.label_precio.config(text=precio_producto)

        # Mostrar la descripción del producto seleccionado
        # self.label_descripcion.config(text=descripcion_producto)

    def crear_widgets_productos(self):
        # Iterar sobre los productos y crear widgets para cada uno
        for i, producto in enumerate(self.productos):
            pass
            """# Obtener la imagen del producto desde la URL y crear el widget de la imagen
            imagen_widget = self.mostrar_imagen_producto(producto["image"])

            # Crear un botón para agregar el producto a la compra
            boton_agregar = tk.Button(self.frame_productos, text="Agregar",
                                      command=lambda producto=producto: self.agregar_producto(producto))
            boton_agregar.grid(row=i, column=0)

            # Mostrar la imagen del producto
            imagen_widget.grid(row=i, column=1)

            # Agregar el nombre y el precio del producto como etiquetas
            nombre_producto = tk.Label(self.frame_productos, text=producto["name"])
            nombre_producto.grid(row=i, column=2)

            precio_producto = tk.Label(self.frame_productos, text=str(producto["price"]))
            precio_producto.grid(row=i, column=3)"""

    def agregar_producto(self):
        # Obtener el producto seleccionado
        producto_seleccionado = self.combo_producto.get()

        # Buscar el producto seleccionado en la lista de productos
        for producto in self.productos:
            if producto["name"] == producto_seleccionado:
                precio_producto = round(producto["price"], 2)
                referencia_ean = producto["ean"]
                id = producto["id"]
                break
        else:
            # Si el producto seleccionado no se encuentra, asignar precio cero
            precio_producto = 0
            referencia_ean = 0

        # Obtener la cantidad y convertirla a un número de punto flotante
        cantidad_str = self.entry_cantidad.get()
        try:
            cantidad = int(cantidad_str)
        except ValueError:
            cantidad = 0

        # print("Producto seleccionado:", producto_seleccionado)
        # print("Precio del producto:", precio_producto)
        # print("Cantidad:", cantidad)

        self.total.set(self.total.get() + precio_producto * cantidad)
        # print("Total actualizado:", self.total.get())

        # Agregar información del producto al resumen en formato de tabla
        self.tree_resumen.insert("", tk.END, values=(id, referencia_ean, producto_seleccionado, cantidad, precio_producto, (precio_producto * cantidad)))

        # Reproducir sonido al agregar un producto
        if self.sonido_activado:
            pygame.mixer.music.load("beep.wav")
            pygame.mixer.music.play()

    def generar_factura(self):
        # Obtener los datos de la factura
        cliente = self.cliente.get()
        productos = self.tree_resumen
        cantidad = self.entry_cantidad.get()
        total = self.total.get()
        date_add = datetime.now()
        ticket_number = random.randint(0,1000)

        """# if you want the button to disappear:
        # button.destroy() or button.pack_forget()
        label = tk.Label(root, text="Hey whatsup bro, i am doing something very interresting.")
        # this creates a new label to the GUI
        label.pack()"""

        # Imprimir encabezado
        print("=== Ticket de Compra ===\n")
        print("Datos de la empresa: Nombre, telefono, razon social, nif")
        print("Factura simplificada N:XXXXXX")
        print(date_add.strftime("Fecha:%d/%m/%Y Hora:%H:%M,%S"))

        # Imprimir la factura (en este caso, simplemente imprimimos en la consola)
        print("Cliente:", cliente)
        print("Productos seleccionados:")
        print(productos)
        print(cantidad)
        print("Total:", total)
        print("Codigo de ticket:", ticket_number)
        print("=== Ticket de Compra ===\n")

    def mostrar_datos_factura(self):
        # Crear una nueva ventana para mostrar los datos del ticket
        self.ventana_factura = tk.Toplevel()
        self.ventana_factura.title("Factura")

        # Definir el tamaño de la ventana y quitar la cabecera del SO
        self.ventana_factura.geometry("800x600")
        self.ventana_factura.overrideredirect(True)

        # Mostrar los datos del ticket en la nueva ventana
        tk.Label(self.ventana_factura, text="Datos del Ticket").grid(row=0, column=0, columnspan=2)

        # Obtener los datos del ticket
        cliente = self.cliente.get()
        total = self.total.get()
        productos = []
        for item in self.tree_resumen.get_children():
            valores = self.tree_resumen.item(item, 'values')
            productos.append(valores)

        # Mostrar los datos del ticket en etiquetas
        tk.Label(self.ventana_factura, text="Cliente:").grid(row=1, column=0, sticky="e")
        tk.Label(self.ventana_factura, text=cliente).grid(row=1, column=1, sticky="w")
        tk.Label(self.ventana_factura, text="Total:").grid(row=2, column=0, sticky="e")
        tk.Label(self.ventana_factura, text=total).grid(row=2, column=1, sticky="w")
        tk.Label(self.ventana_factura, text="Productos:").grid(row=3, column=0, sticky="e")
        for i, producto in enumerate(productos):
            tk.Label(self.ventana_factura, text=f"{producto[1]} - Cantidad: {producto[2]} - Precio: {producto[3]}").grid(row=3+i, column=1, sticky="w")

        # Botones de Cobrar y Cancelar
        tk.Button(self.ventana_factura, text="Cobrar", command=self.cobrar).grid(row=4+len(productos), column=0, padx=5, pady=5)
        tk.Button(self.ventana_factura, text="Cancelar", command=self.ventana_factura.destroy).grid(row=4+len(productos), column=1, padx=5, pady=5)

    def cobrar(self):
        # Obtener los datos del ticket
        cliente_id = self.cliente.get()  # ID del cliente
        pago = "efectivo"
        productos = self.tree_resumen.get_children()
        total_pagado = self.total.get()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Crear listas separadas para los IDs de los productos y las cantidades
        id_productos = []
        cantidades = []

        # Iterar sobre los elementos del Treeview y obtener los IDs de los productos y las cantidades
        for item in productos:
            valores = self.tree_resumen.item(item, 'values')
            id_producto = valores[0]  # ID del producto
            cantidad = valores[3]  # Cantidad
            id_productos.append(id_producto)
            cantidades.append(cantidad)

        # Crear un diccionario con las listas de IDs de productos y cantidades
        datos_ticket = {"id_product": id_productos, "quantity": cantidades}
        datos_json = json.dumps(datos_ticket)

        # Guardar los datos del ticket en la base de datos
        # Guarda el ticket y obtén el ID del ticket recién insertado
        ticket_id = self.db.guardar_ticket(cliente_id, pago, datos_json, total_pagado, fecha_actual)

        # Mostrar un mensaje de confirmación
        messagebox.showinfo("Cobro", "El cobro se ha realizado con éxito.")

        # Enviar los datos al webservice
        carrito_id = self.webservice.crear_carrito(cliente_id, datos_ticket)
        if carrito_id:
            print(f"Datos del carrito enviados correctamente al webservice. ID del carrito: {carrito_id}")
            pedido_id = self.webservice.crear_pedido(carrito_id, cliente_id, total_pagado)
            if pedido_id:
                print(f"Pedido creado correctamente. ID del pedido: {pedido_id}")

        # Guardar los datos del pedido en la base de datos
        self.db.guardar_order(ticket_id, carrito_id, pedido_id)
        messagebox.showinfo("Actualización", "Datos enviados correctamente a su tiendda online.")

        # Reiniciar la interfaz para el próximo cliente
        self.tree_resumen.delete(*self.tree_resumen.get_children())
        self.total.set(0)
        self.cliente.set(0)
        self.entry_ean.focus_set()

    def imprimir_ticket(self):
        """# Crear una instancia de la impresora USB (asegúrate de conectar la impresora a través de USB)
        p = Usb(0x0456, 0x0808, 0)

        # Configurar la impresora (opcional)
        p.set(align='center', font='b', text_type='normal', width=1, height=1)"""

        """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
        p = Usb(0x04b8, 0x0202, 0, profile="TM-T88III")

        # Imprimir encabezado
        p.text("=== Ticket de Compra ===\n")

        p.text("Hello World\n")
        p.image("logo.gif")
        p.barcode('1324354657687', 'EAN13', 64, 2, '', '')
        p.cut()

    def limpiar_ventana_principal(self):
        # Limpiar los valores de los widgets en la ventana principal
        self.combo_cliente.set("")  # Limpiar el combobox de clientes
        self.entry_ean.delete(0, tk.END)  # Limpiar el campo de entrada de EAN
        self.combo_producto.set("")  # Limpiar el combobox de productos
        self.label_nombre.config(text="")  # Limpiar la etiqueta de nombre de producto
        self.label_precio.config(text="")  # Limpiar la etiqueta de precio de producto
        self.entry_cantidad.delete(0, tk.END)  # Limpiar el campo de entrada de cantidad
        self.tree_resumen.delete(*self.tree_resumen.get_children())  # Limpiar el resumen de productos
        self.total.set(0)  # Reiniciar el total a cero

    def buscar_por_ean(self):
        ean = self.entry_ean.get()

        # Buscar el producto por EAN en la lista de productos
        for producto in self.productos:
            if producto["ean"] == int(ean):
                self.combo_producto.set(producto["name"])  # Seleccionar el producto en el combobox
                return

        # Si no se encuentra el producto, mostrar un mensaje de error
        messagebox.showerror("Error", "Producto no encontrado para el EAN proporcionado")

def main():
    root = tk.Tk()
    root.configure(background='#eeeeee')
    # root.overrideredirect(True)  # turns off title bar, geometry

    # root.attributes('-alpha', 0.9) # añade transparencia
    size = '%dx%d+%d+%d' % (1280, 900, 0, 0)
    root.geometry(size)
    # root.resizable(width=False, height=False)  # bloquea agrandar ventana

    # root.state('zoomed') # maximiza la pantalla
    # root.overrideredirect(True)
    # root.overrideredirect(False)
    # root.attributes('-fullscreen', True)
    app = TPVApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()