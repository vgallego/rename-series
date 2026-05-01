# Renombrador de Series para Plex

Herramienta gráfica para renombrar archivos de series de TV de forma compatible con Plex, usando patrones inteligentes de detección de capítulos.

## Características

- **Interfaz gráfica simple** con Tkinter
- **Detección automática de números de capítulo** usando múltiples patrones regex
- **Soporte para diversos formatos de nombres** (S##E##, ##x##, Cap##, [###], etc.)
- **Limpieza automática de ruido** (resoluciones, etiquetas de subs, webs, etc.)
- **Formato de salida estándar Plex**: `NombreSerie S#x##.ext`
- **Validaciones** para evitar sobrescrituras y permisos denegados

## Requisitos

- Python 3.6+
- Tkinter (incluido en Python en Windows, macOS; en Linux: `python3-tk`)

## Instalación y uso

### 1. Ejecutar directamente

```bash
python rename-series.py
```

### 2. Construir ejecutable (requiere PyInstaller)

```bash
pip install pyinstaller
pyinstaller RenombradorSeries.spec
```

## Interfaz gráfica

La aplicación presenta una ventana con 3 campos:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Archivos a renombrar** | Click en "Seleccionar" para elegir uno o más archivos | `5 archivo(s) seleccionado(s)` |
| **Nombre de la serie** | Nombre exacto de la serie (como aparecerá en el resultado) | `Breaking Bad` |
| **Temporada** | Número de temporada (entero) | `1` |

Una vez completados los campos, click en "Iniciar Renombrado".

## Patrones soportados

La herramienta detecta automáticamente el número de capítulo de múltiples formatos:

### Patrones principales

| Patrón | Ejemplo | Nota |
|--------|---------|------|
| `S##E##` / `s##e##` | `S01E05`, `s1e3` | Captura temporada y capítulo |
| `##x##` | `1x05`, `12x03` | Captura temporada y capítulo |
| `Cap##` / `Cap.##` | `Cap.05`, `Cap 12` | Etiqueta explícita |
| `[###]` | `[001]`, `[105]` | Entre corchetes |
| `Episode ##` | `Episode 5` | Etiqueta explícita |

### Patrones con separadores

| Patrón | Ejemplo |
|--------|---------|
| `##.` (punto) | `05.mkv` |
| `._##._` | `video_05_part.mkv` |
| `_##_` / `_###_` | `_05_episodio.mkv` |
| `_##.` / `_###.` | `_05.mkv` |

### Notas sobre patrones de 3 dígitos

Los números de 3 dígitos (`###`) se convierten a 2 usando módulo 100:
- `001` → `01`
- `523` → `23` 
- `101` → `01`

## Limpieza automática

Antes de buscar patrones, la herramienta elimina automáticamente:

### Resoluciones y códecs
- Resoluciones: `720p`, `1080p`, `2160p`, `480p`
- Compresión: `h264`, `x264`, `x265`, `hevc`
- Audio: `ac3`, `dts`
- Formatos: `hdtv`, `web-dl`, `webrip`, `bluray`

### Ruido y etiquetas
- URLs: `www.*`
- Sitios: `newpct1`, `by.*`
- Subtítulos: `[subs]`, `subs`, etc.
- Caracteres especiales: Se normalizan espacios y separadores

## Ejemplos de renombrado

### Entrada: `Breaking.Bad.S01E05.720p.hdtv-grupo.mkv`

```
Nombre serie: Breaking Bad
Temporada: 1
↓
Salida: Breaking Bad 1x05.mkv
```

### Entrada: `SerieX_01_Episodio_Completo.avi`

```
Nombre serie: Serie X
Temporada: 2
↓
Salida: Serie X 2x01.avi
```

### Entrada: `Cap.10[1080p].mp4`

```
Nombre serie: Mi Serie
Temporada: 3
↓
Salida: Mi Serie 3x10.mp4
```

## Comportamiento y mensajes

- **Saltado (no es fichero)**: El archivo seleccionado es una carpeta, se omite
- **No se pudo extraer el número de capítulo**: El nombre no coincide con ningún patrón
- **Saltado (ya existe destino)**: Ya existe un archivo con ese nombre, se omite para evitar sobrescrituras
- **Permiso denegado**: El sistema no permite renombrar el archivo (permisos insuficientes)
- **Completado**: Todos los archivos se renombraron exitosamente

## Estructura del código

### Funciones principales

- `limpiar_nombre(nombre: str) -> str`: Limpia ruido y normaliza el nombre antes de buscar patrones
- `extraer_numero_capitulo(nombre_archivo: str) -> int | None`: Detecta el número de capítulo usando los patrones regex
- `renombrar_archivos(archivos, nombre_serie, temporada)`: Procesa la lista de archivos y los renombra
- `seleccionar_archivos()`: Abre diálogo para seleccionar archivos
- `iniciar_renombrado()`: Valida inputs y ejecuta el renombrado

### Variables globales

- `PATRONES`: Lista de patrones regex para detectar capítulos (tuplas: regex, grupo, descripción)
- `RESOLUCIONES`: Tokens a eliminar (resoluciones, códecs)
- `RUIDO`: Patrones regex para eliminar spam/URLs
- `selected_files`: Almacena rutas de archivos seleccionados (no se parsea el Entry)

## Configuración

Edita las constantes en el código para:

- **Agregar patrones**: Añade tuplas a `PATRONES` con el formato `(regex, grupo_capítulo, descripción)`
- **Eliminar resoluciones**: Modifica `RESOLUCIONES` si deseas mantener ciertos tokens
- **Agregar patrones de ruido**: Añade regex a `RUIDO` para filtrar más etiquetas

## Notas técnicas

- Los patrones usan **lookahead/lookbehind negativo** para evitar capturar dígitos adyacentes
- La búsqueda es **case-insensitive** (`re.IGNORECASE`)
- El nombre final sigue el formato estándar Plex: `{Nombre} {T}x{E:02d}.{ext}`
- El número de capítulo siempre se formatea con 2 dígitos (`{E:02d}`)

## Licencia

Uso libre para propósitos personales.
