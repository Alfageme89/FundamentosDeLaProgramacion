"""
gestor_archivos.py
==================
Módulo de entrada/salida de datos con archivos TXT, CSV y JSON.
Cubre el RA5: Librerías de entrada y salida.

Funciones:
    TXT  → guardar_cursos_txt / cargar_cursos_txt
    CSV  → exportar_recursos_csv / importar_recursos_csv
    JSON → guardar_configuracion_json / cargar_configuracion_json
"""

import csv
import json
import os
from modelos import (
    Curso, RecursoMultimedia, RecursoTexto,
    RecursoImagen, RecursoAudio, RecursoVideo,
)

# ─────────────────────────────────────────────────────────────
# Rutas de archivos por defecto
# ─────────────────────────────────────────────────────────────
RUTA_CURSOS_TXT    = "cursos.txt"
RUTA_RECURSOS_CSV  = "recursos.csv"
RUTA_CONFIG_JSON   = "configuracion.json"


# ═════════════════════════════════════════════════════════════
# RA5 ▶ Gestión de archivos TXT  (cursos.txt)
# ═════════════════════════════════════════════════════════════

def guardar_cursos_txt(cursos: list, ruta: str = RUTA_CURSOS_TXT) -> None:
    """
    Guarda la lista de cursos en un archivo de texto plano.
    Cada curso ocupa un bloque separado por líneas '---'.

    Args:
        cursos: Lista de objetos Curso.
        ruta:   Ruta del archivo de destino.
    """
    # RA5: uso de 'with open' para apertura segura
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("# CURSOS REGISTRADOS EN LA PLATAFORMA EDUCATIVA\n")
        f.write(f"# Total de cursos: {len(cursos)}\n")
        f.write("=" * 60 + "\n")
        for curso in cursos:
            f.write(f"ID          : {curso.id}\n")
            f.write(f"Título      : {curso.titulo}\n")
            f.write(f"Unidad      : {curso.unidad}\n")
            f.write(f"Descripción : {curso.descripcion}\n")
            f.write(f"Creado      : {curso.fecha_creacion}\n")
            f.write(f"Recursos    : {len(curso.recursos)}\n")
            f.write("---\n")
    print(f"  ✓ Cursos guardados en '{ruta}' ({len(cursos)} registros).")


def cargar_cursos_txt(ruta: str = RUTA_CURSOS_TXT) -> list[dict]:
    """
    Lee el archivo TXT de cursos y devuelve una lista de diccionarios.
    No recrea objetos Curso para evitar duplicar el contador de ID.

    Args:
        ruta: Ruta del archivo a leer.

    Returns:
        Lista de diccionarios con los campos de cada curso.
    """
    if not os.path.exists(ruta):
        print(f"  ⚠  Archivo '{ruta}' no encontrado.")
        return []

    cursos_leidos: list[dict] = []
    curso_actual: dict = {}

    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            # Saltar comentarios y separadores
            if linea.startswith("#") or linea.startswith("="):
                continue
            if linea == "---":
                if curso_actual:
                    cursos_leidos.append(curso_actual)
                    curso_actual = {}
                continue
            if ":" in linea:
                clave, _, valor = linea.partition(":")
                curso_actual[clave.strip().lower()] = valor.strip()

    print(f"  ✓ {len(cursos_leidos)} cursos leídos desde '{ruta}'.")
    return cursos_leidos


# ═════════════════════════════════════════════════════════════
# RA5 ▶ Gestión de archivos CSV  (recursos.csv)
# ═════════════════════════════════════════════════════════════

# Campos que aparecerán en el CSV
CAMPOS_CSV = ["id", "titulo", "descripcion", "url", "id_curso", "tipo", "fecha_creacion"]


def exportar_recursos_csv(recursos: list, ruta: str = RUTA_RECURSOS_CSV) -> None:
    """
    Exporta la lista de recursos multimedia a un archivo CSV.

    Args:
        recursos: Lista de objetos RecursoMultimedia.
        ruta:     Ruta del archivo CSV de destino.
    """
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        # RA5: uso del módulo csv con DictWriter
        escritor = csv.DictWriter(f, fieldnames=CAMPOS_CSV, extrasaction="ignore")
        escritor.writeheader()
        for r in recursos:
            escritor.writerow(r.to_dict())
    print(f"  ✓ {len(recursos)} recursos exportados a '{ruta}'.")


def importar_recursos_csv(ruta: str = RUTA_RECURSOS_CSV) -> list[dict]:
    """
    Lee un CSV de recursos y devuelve una lista de diccionarios.

    Args:
        ruta: Ruta del archivo CSV.

    Returns:
        Lista de diccionarios con los campos de cada recurso.
    """
    if not os.path.exists(ruta):
        print(f"  ⚠  Archivo '{ruta}' no encontrado.")
        return []

    filas: list[dict] = []
    with open(ruta, "r", newline="", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            filas.append(dict(fila))

    print(f"  ✓ {len(filas)} recursos importados desde '{ruta}'.")
    return filas


def reconstruir_recurso_desde_dict(datos: dict) -> RecursoMultimedia | None:
    """
    Reconstruye el objeto RecursoMultimedia correcto según el campo 'tipo'.
    Útil al recargar datos desde CSV o BD.

    Args:
        datos: Diccionario con los campos del recurso.

    Returns:
        Instancia de la subclase correspondiente, o None si falla.
    """
    tipo  = datos.get("tipo", "generico")
    titulo = datos.get("titulo", "")
    desc   = datos.get("descripcion", "")
    url    = datos.get("url", "")
    try:
        id_curso = int(datos.get("id_curso", 0))
    except ValueError:
        id_curso = 0

    mapa = {
        "texto":  lambda: RecursoTexto(titulo, desc, url, id_curso),
        "imagen": lambda: RecursoImagen(titulo, desc, url, id_curso),
        "audio":  lambda: RecursoAudio(titulo, desc, url, id_curso),
        "video":  lambda: RecursoVideo(titulo, desc, url, id_curso),
    }

    constructor = mapa.get(tipo)
    if constructor:
        return constructor()
    return RecursoMultimedia(titulo, desc, url, id_curso)


# ═════════════════════════════════════════════════════════════
# RA5 ▶ Gestión de archivos JSON  (configuracion.json)
# ═════════════════════════════════════════════════════════════

CONFIG_DEFECTO: dict = {
    "nombre_plataforma": "EduMedia Platform",
    "version": "1.0.0",
    "idioma": "es",
    "max_recursos_por_curso": 50,
    "formatos_permitidos": ["txt", "pdf", "mp3", "mp4", "jpg", "png"],
    "tema": "oscuro",
}


def guardar_configuracion_json(config: dict, ruta: str = RUTA_CONFIG_JSON) -> None:
    """
    Guarda el diccionario de configuración en un archivo JSON.

    Args:
        config: Diccionario con pares clave-valor de configuración.
        ruta:   Ruta del archivo JSON de destino.
    """
    with open(ruta, "w", encoding="utf-8") as f:
        # indent=4 para legibilidad humana; ensure_ascii=False para tildes
        json.dump(config, f, indent=4, ensure_ascii=False)
    print(f"  ✓ Configuración guardada en '{ruta}'.")


def cargar_configuracion_json(ruta: str = RUTA_CONFIG_JSON) -> dict:
    """
    Lee el archivo JSON de configuración.
    Si no existe, crea uno con los valores por defecto.

    Args:
        ruta: Ruta del archivo JSON.

    Returns:
        Diccionario con la configuración.
    """
    if not os.path.exists(ruta):
        print(f"  ⚠  '{ruta}' no encontrado. Se usará configuración por defecto.")
        guardar_configuracion_json(CONFIG_DEFECTO, ruta)
        return CONFIG_DEFECTO.copy()

    with open(ruta, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
            print(f"  ✓ Configuración cargada desde '{ruta}'.")
            return config
        except json.JSONDecodeError as e:
            print(f"  ✗ Error al leer JSON: {e}. Se usará configuración por defecto.")
            return CONFIG_DEFECTO.copy()


def guardar_preferencias_usuario_json(id_usuario: int, preferencias: dict,
                                      ruta: str = "preferencias.json") -> None:
    """
    Guarda las preferencias de un usuario en un archivo JSON dedicado.
    Si el archivo existe, actualiza sólo la entrada del usuario.

    Args:
        id_usuario:   ID del usuario.
        preferencias: Diccionario con sus preferencias.
        ruta:         Ruta del archivo JSON.
    """
    # Cargar existente o crear vacío
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = {}
    else:
        datos = {}

    datos[str(id_usuario)] = preferencias

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
    print(f"  ✓ Preferencias del usuario {id_usuario} guardadas en '{ruta}'.")


def cargar_preferencias_usuario_json(id_usuario: int,
                                     ruta: str = "preferencias.json") -> dict:
    """
    Carga las preferencias de un usuario específico desde JSON.

    Args:
        id_usuario: ID del usuario.
        ruta:       Ruta del archivo JSON.

    Returns:
        Diccionario con sus preferencias, o vacío si no existen.
    """
    if not os.path.exists(ruta):
        return {}
    with open(ruta, "r", encoding="utf-8") as f:
        try:
            datos = json.load(f)
            return datos.get(str(id_usuario), {})
        except json.JSONDecodeError:
            return {}


# ═════════════════════════════════════════════════════════════
# RA5 ▶ Utilidad: mostrar diferencias entre formatos
# ═════════════════════════════════════════════════════════════

def explicar_formatos() -> None:
    """Muestra en consola la diferencia entre TXT, CSV y JSON (defensa RA5)."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          DIFERENCIAS ENTRE FORMATOS DE ARCHIVO               ║
╠══════════════════════════════════════════════════════════════╣
║  TXT  │ Texto libre, legible. Ideal para logs y resúmenes.   ║
║       │ Sin estructura fija; parse manual.                    ║
╠───────┼────────────────────────────────────────────────────  ║
║  CSV  │ Valores separados por comas. Ideal para tablas y      ║
║       │ exportar a Excel/Calc. Estructura plana.              ║
╠───────┼────────────────────────────────────────────────────  ║
║  JSON │ Objetos/listas anidados. Ideal para configuraciones   ║
║       │ y APIs. Legible y estructurado. Nativo en Python      ║
║       │ con el módulo 'json'.                                  ║
╚══════════════════════════════════════════════════════════════╝
""")
