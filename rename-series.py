import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# Lista de patrones y grupo a extraer (expresión regular, grupo)
PATRONES = [
    # Patrones prioritarios (formato explícito temporada-episodio)
    (r'\bS(\d{1,2})E(\d{1,2})\b', 2),          # S01E03, S2E15
    (r'\b(\d{1,2})x(\d{1,2})\b', 2),           # 2x03, 01x15
    
    # Patrones generales de capítulos
    (r'Cap[\.\s](\d{2,3})', 1),            # [Cap.101], [Cap 203]
    (r'\bCap[\.\s](\d{3})\b', 1),               # Cap.101, Cap205
    (r'\[(\d{3})\]', 1),                        # [105], [207]
    (r'\b(\d{3})(?!p)\b', 1),                   # 101, 305 (excluye 720p)
    
    # Patrones alternativos
    (r'\bEpisode\s*(\d{1,2})\b', 1),            # Episode 03, Episode 15
    (r'\b(\d{2})\.', 1),                        # 03.mkv, 15.avi
    (r'[\._\-](\d{2})[\._\-]', 1)               # _03_, -15-
]

RESOLUCIONES = ["720p", "1080p", "2160p", "480p", "HDTV", "WEB-DL", "h264", "AC3"]

def limpiar_nombre(nombre):
    """Limpia el nombre de elementos que interfieren"""
    nombre = re.sub(r'[\[\]\(\)]', '', nombre)  # Elimina corchetes y paréntesis
    for elemento in RESOLUCIONES:
        nombre = re.sub(r'\b' + re.escape(elemento) + r'\b', '', nombre, flags=re.IGNORECASE)
    return nombre.strip()

def extraer_numero_capitulo(nombre_archivo):
    """Extrae el número de episodio usando múltiples patrones"""
    nombre_limpio = limpiar_nombre(nombre_archivo)
    
    for patron, grupo in PATRONES:
        try:
            match = re.search(patron, nombre_limpio, re.IGNORECASE)
            if match:
                numero = int(match.group(grupo))
                
                # Manejar diferentes formatos numéricos
                if 100 <= numero <= 999:  # Si es de 3 dígitos (101, 203, etc)
                    return numero % 100
                return numero
        except:
            continue
    return None

def renombrar_archivos(archivos, nombre_serie, temporada):
    for archivo in archivos:
        try:
            nombre_base = os.path.basename(archivo)
            base, ext = os.path.splitext(nombre_base)
            
            numero_capitulo = extraer_numero_capitulo(base)
            if numero_capitulo is None:
                print(f"No se pudo extraer el número de capítulo de {archivo}")
                continue
            
            # Formatear nuevo nombre
            nuevo_nombre = f"{nombre_serie} {temporada}x{numero_capitulo:02d}{ext}"
            directorio = os.path.dirname(archivo)
            nueva_ruta = os.path.join(directorio, nuevo_nombre)
            
            os.rename(archivo, nueva_ruta)
            print(f"Renombrado: {archivo} -> {nueva_ruta}")
            
        except Exception as e:
            print(f"Error procesando {archivo}: {str(e)}")

# El resto del código de la interfaz gráfica permanece igual
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