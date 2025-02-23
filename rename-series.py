import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

def renombrar_archivos(archivos, nombre_serie, temporada):
    for archivo in archivos:
        try:
            # Extraer nombre base y extensión
            nombre_base = os.path.basename(archivo)
            base, extension = os.path.splitext(nombre_base)
            
            # Buscar el número de capítulo en el formato [Cap.XXX]
            match = re.search(r'\[Cap\.(\d+)\]', base, re.IGNORECASE)
            if not match:
                print(f"Formato no válido: {archivo}")
                continue
                
            numero_capitulo = int(match.group(1))
            numero_episodio = numero_capitulo % 100  # Tomar últimos dos dígitos
            
            # Formatear nuevo nombre
            nuevo_nombre = f"{nombre_serie} {temporada}x{numero_episodio:02d}{extension}"
            directorio = os.path.dirname(archivo)
            nueva_ruta = os.path.join(directorio, nuevo_nombre)
            
            # Renombrar el archivo
            os.rename(archivo, nueva_ruta)
            print(f"Renombrado: {archivo} -> {nueva_ruta}")
            
        except Exception as e:
            print(f"Error procesando {archivo}: {str(e)}")

def seleccionar_archivos():
    archivos = filedialog.askopenfilenames(title="Selecciona los archivos de la serie")
    if archivos:
        entry_archivos.delete(0, tk.END)
        entry_archivos.insert(0, ", ".join(archivos))

def iniciar_renombrado():
    try:
        archivos = entry_archivos.get().split(", ")
        nombre_serie = entry_nombre_serie.get()
        temporada = int(entry_temporada.get())
        
        if not archivos or not nombre_serie:
            raise ValueError("Faltan datos requeridos")
            
        renombrar_archivos(archivos, nombre_serie.strip(), temporada)
        messagebox.showinfo("Completado", "Archivos renombrados correctamente")
        
    except ValueError as e:
        messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Renombrador de Series para Plex")
root.geometry("600x300")

# Controles de la interfaz
tk.Label(root, text="Archivos a renombrar:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_archivos = tk.Entry(root, width=60)
entry_archivos.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Seleccionar", command=seleccionar_archivos).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Nombre de la serie:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_nombre_serie = tk.Entry(root, width=60)
entry_nombre_serie.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Temporada:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_temporada = tk.Entry(root, width=10)
entry_temporada.grid(row=2, column=1, padx=5, pady=5, sticky="w")

btn_renombrar = tk.Button(root, text="Iniciar Renombrado", command=iniciar_renombrado)
btn_renombrar.grid(row=3, column=1, pady=15)

root.mainloop()