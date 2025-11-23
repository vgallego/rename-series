import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# ---- Robust regex patterns (work even when glued to letters/digits) ----
PATRONES = [
    # Season/Episode explicit formats
    (r'(?<!\d)[sS](\d{1,2})[ ._\-]*[eE](\d{1,2})(?!\d)', 2),   # S01E03, S2E15, S01.E03, etc.
    (r'(?<!\d)(\d{1,2})x(\d{1,2})(?!\d)', 2),                  # 1x01, 02x10 (also glued like Name1x01)

    # Compressed 3-digit SxEE (e.g., 104 -> S1E04). Excludes things like 720p via (?!\d|p)
    (r'(?<!\d)(\d{3})(?!\d|p)', 1),                            # 101, 305 (not followed by digit or 'p')

    # Spanish/other alternatives
    (r'Cap[\.\s](\d{2,3})', 1),
    (r'\[(\d{3})\]', 1),
    (r'\bEpisode\s*(\d{1,2})\b', 1),
    (r'\b(\d{2})\.', 1),
    (r'[\._\-](\d{2})[\._\-]', 1),
    (r'_(\d{2,3})_', 1),
    (r'_(\d{2,3})\.', 1),
]

# Tokens to remove (we'll strip them even if glued to digits/letters)
RESOLUCIONES = [
    "720p", "1080p", "2160p", "480p",
    "hdtv", "web-dl", "web dl", "webrip", "bluray",
    "h264", "x264", "x265", "hevc",
    "ac3", "dts"
]

# Optional: common site/release noise to strip
RUIDO = [
    r'www\.[^\s]+',     # www.newpct1.com, etc.
    r'newpct1', r'by\.[^\s]+', r'\[.*?subs?.*?\]', r'\bsubs?\b'
]

def limpiar_nombre(nombre: str) -> str:
    """Clean noisy tokens before regex matching."""
    # Remove brackets but keep content inside removed earlier by design
    nombre = re.sub(r'[\[\]\(\)]', ' ', nombre)

    # Remove resolution tokens even if glued to digits/letters
    for elemento in RESOLUCIONES:
        nombre = re.sub(re.escape(elemento), ' ', nombre, flags=re.IGNORECASE)

    # Remove common noise patterns (websites, tags)
    for patron in RUIDO:
        nombre = re.sub(patron, ' ', nombre, flags=re.IGNORECASE)

    # Normalize separators to spaces
    nombre = re.sub(r'[.\-_\s]+', ' ', nombre)
    # Collapse multiple spaces
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    return nombre

def extraer_numero_capitulo(nombre_archivo: str):
    """Extract episode number using multiple patterns."""
    nombre_limpio = limpiar_nombre(nombre_archivo)

    for patron, grupo in PATRONES:
        m = re.search(patron, nombre_limpio, re.IGNORECASE)
        if m:
            try:
                num = int(m.group(grupo))
            except ValueError:
                continue
            # For compressed 3-digit SxEE (e.g., 104 -> episode 4)
            if num >= 100:
                return num % 100
            return num
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

            # Format new name: "<Serie> <Temporada>x<EE>"
            nuevo_nombre = f"{nombre_serie} {temporada}x{numero_capitulo:02d}{ext}"
            directorio = os.path.dirname(archivo)
            nueva_ruta = os.path.join(directorio, nuevo_nombre)

            # Avoid overwriting
            if os.path.exists(nueva_ruta):
                print(f"Saltado (ya existe destino): {nueva_ruta}")
                continue

            os.rename(archivo, nueva_ruta)
            print(f"Renombrado: {archivo} -> {nueva_ruta}")

        except PermissionError as e:
            print(f"Permiso denegado renombrando {archivo}: {e}")
        except Exception as e:
            print(f"Error procesando {archivo}: {str(e)}")

# --- GUI (unchanged structure) ---
def seleccionar_archivos():
    archivos = filedialog.askopenfilenames(title="Selecciona los archivos de la serie")
    if archivos:
        entry_archivos.delete(0, tk.END)
        entry_archivos.insert(0, ", ".join(archivos))

def iniciar_renombrado():
    try:
        archivos_raw = entry_archivos.get().strip()
        if not archivos_raw:
            raise ValueError("Selecciona al menos un archivo.")
        # Split robustly on ", " or "," with optional spaces
        archivos = [a.strip() for a in re.split(r',\s*', archivos_raw) if a.strip()]

        nombre_serie = entry_nombre_serie.get().strip()
        if not nombre_serie:
            raise ValueError("Introduce el nombre de la serie.")

        temporada = int(entry_temporada.get())
        renombrar_archivos(archivos, nombre_serie, temporada)
        messagebox.showinfo("Completado", "Archivos renombrados correctamente")

    except ValueError as e:
        messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

# GUI setup
root = tk.Tk()
root.title("Renombrador de Series para Plex")
root.geometry("600x300")

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
