import subprocess
import sys

def actualizar_base_de_datos():
    try:
        python_executable = sys.executable
        productos = subprocess.run([python_executable, "updateProducts.py"], capture_output=True, text=True)
        clientes = subprocess.run([python_executable, "updateCustomers.py"], capture_output=True, text=True)

        salida_actualizacion = productos.stdout + clientes.stdout
        return salida_actualizacion
    except Exception as e:
        return f"Error al actualizar la base de datos:\n{str(e)}"