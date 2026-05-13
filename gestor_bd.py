"""
gestor_bd.py
============
Módulo de acceso a datos con SQLite.
Cubre el RA6: Acceso a datos y bases de datos relacionales.

Funciones principales:
    - crear_tablas()
    - insertar_curso() / insertar_recurso() / insertar_usuario()
    - consultar_cursos() / consultar_recursos() / consultar_usuarios()
    - actualizar_curso() / actualizar_recurso()
    - eliminar_curso() / eliminar_recurso()
    - cargar_masivo_recursos()
    - sincronizar_plataforma()
"""

import sqlite3
import os
from typing import Optional

# ─────────────────────────────────────────────────────────────
# RA6 ▶ Configuración de la base de datos
# ─────────────────────────────────────────────────────────────
RUTA_BD = "plataforma.db"


def obtener_conexion(ruta: str = RUTA_BD) -> sqlite3.Connection:
    """
    Crea y devuelve una conexión a SQLite.
    Activa el soporte de claves foráneas (PRAGMA).

    Returns:
        Objeto Connection de sqlite3.
    """
    conn = sqlite3.connect(ruta)
    conn.execute("PRAGMA foreign_keys = ON")
    # Devolver filas como objetos tipo dict con acceso por nombre
    conn.row_factory = sqlite3.Row
    return conn


# ═════════════════════════════════════════════════════════════
# RA6 ▶ Creación de tablas
# ═════════════════════════════════════════════════════════════

SQL_CREAR_TABLA_CURSOS = """
CREATE TABLE IF NOT EXISTS cursos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo          TEXT    NOT NULL,
    unidad          TEXT    NOT NULL,
    descripcion     TEXT,
    fecha_creacion  TEXT
);
"""

SQL_CREAR_TABLA_RECURSOS = """
CREATE TABLE IF NOT EXISTS recursos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo          TEXT    NOT NULL,
    descripcion     TEXT,
    url             TEXT,
    tipo            TEXT    NOT NULL DEFAULT 'generico',
    id_curso        INTEGER NOT NULL,
    fecha_creacion  TEXT,
    FOREIGN KEY (id_curso) REFERENCES cursos(id) ON DELETE CASCADE
);
"""

SQL_CREAR_TABLA_USUARIOS = """
CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL,
    email           TEXT    UNIQUE NOT NULL,
    rol             TEXT    NOT NULL DEFAULT 'estudiante',
    fecha_registro  TEXT
);
"""


def crear_tablas(ruta: str = RUTA_BD) -> None:
    """
    Crea las tablas cursos, recursos y usuarios si no existen.
    Opera con consultas parametrizadas seguras (RA6).
    """
    with obtener_conexion(ruta) as conn:
        conn.execute(SQL_CREAR_TABLA_CURSOS)
        conn.execute(SQL_CREAR_TABLA_RECURSOS)
        conn.execute(SQL_CREAR_TABLA_USUARIOS)
        conn.commit()
    print(f"  ✓ Tablas verificadas/creadas en '{ruta}'.")


# ═════════════════════════════════════════════════════════════
# RA6 ▶ Operaciones CRUD — CURSOS
# ═════════════════════════════════════════════════════════════

def insertar_curso(titulo: str, unidad: str, descripcion: str,
                   fecha_creacion: str = "", ruta: str = RUTA_BD) -> int:
    """
    Inserta un nuevo curso en la BD con consulta parametrizada.

    Returns:
        ID del curso insertado.
    """
    sql = """
        INSERT INTO cursos (titulo, unidad, descripcion, fecha_creacion)
        VALUES (?, ?, ?, ?)
    """
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute(sql, (titulo, unidad, descripcion, fecha_creacion))
        conn.commit()
        return cursor.lastrowid


def consultar_cursos(ruta: str = RUTA_BD) -> list[dict]:
    """
    Recupera todos los cursos de la BD.

    Returns:
        Lista de diccionarios con los campos de cada curso.
    """
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute("SELECT * FROM cursos ORDER BY id")
        return [dict(fila) for fila in cursor.fetchall()]


def consultar_curso_por_id(id_curso: int, ruta: str = RUTA_BD) -> Optional[dict]:
    """Recupera un curso por su ID."""
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute("SELECT * FROM cursos WHERE id = ?", (id_curso,))
        fila = cursor.fetchone()
        return dict(fila) if fila else None


def buscar_cursos_bd(termino: str, ruta: str = RUTA_BD) -> list[dict]:
    """Busca cursos por título o unidad usando LIKE (RA6: SELECT con parámetros)."""
    patron = f"%{termino}%"
    sql = "SELECT * FROM cursos WHERE titulo LIKE ? OR unidad LIKE ? ORDER BY id"
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute(sql, (patron, patron))
        return [dict(f) for f in cursor.fetchall()]


def actualizar_curso(id_curso: int, titulo: str, unidad: str,
                     descripcion: str, ruta: str = RUTA_BD) -> bool:
    """
    Actualiza los datos de un curso existente (RA6: UPDATE parametrizado).

    Returns:
        True si se modificó algún registro, False si no existe.
    """
    sql = """
        UPDATE cursos
        SET titulo = ?, unidad = ?, descripcion = ?
        WHERE id = ?
    """
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute(sql, (titulo, unidad, descripcion, id_curso))
        conn.commit()
        return cursor.rowcount > 0


def eliminar_curso(id_curso: int, ruta: str = RUTA_BD) -> bool:
    """
    Elimina un curso y sus recursos asociados (CASCADE activado).

    Returns:
        True si se eliminó, False si no existía.
    """
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute("DELETE FROM cursos WHERE id = ?", (id_curso,))
        conn.commit()
        return cursor.rowcount > 0


# ═════════════════════════════════════════════════════════════
# RA6 ▶ Operaciones CRUD — RECURSOS
# ═════════════════════════════════════════════════════════════

def insertar_recurso(titulo: str, descripcion: str, url: str, tipo: str,
                     id_curso: int, fecha_creacion: str = "",
                     ruta: str = RUTA_BD) -> int:
    """
    Inserta un recurso multimedia usando consulta parametrizada.

    Returns:
        ID del recurso insertado.
    """
    sql = """
        INSERT INTO recursos (titulo, descripcion, url, tipo, id_curso, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute(sql, (titulo, descripcion, url, tipo, id_curso, fecha_creacion))
        conn.commit()
        return cursor.lastrowid


def consultar_recursos(tipo: Optional[str] = None, ruta: str = RUTA_BD) -> list[dict]:
    """
    Recupera recursos, opcionalmente filtrados por tipo.

    Args:
        tipo: 'texto', 'imagen', 'audio', 'video' o None para todos.
    """
    if tipo:
        sql = "SELECT * FROM recursos WHERE tipo = ? ORDER BY id"
        params = (tipo,)
    else:
        sql = "SELECT * FROM recursos ORDER BY id"
        params = ()
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute(sql, params)
        return [dict(f) for f in cursor.fetchall()]


def consultar_recursos_por_curso(id_curso: int, ruta: str = RUTA_BD) -> list[dict]:
    """Devuelve todos los recursos de un curso concreto."""
    sql = "SELECT * FROM recursos WHERE id_curso = ? ORDER BY id"
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute(sql, (id_curso,))
        return [dict(f) for f in cursor.fetchall()]


def actualizar_recurso_url(id_recurso: int, nueva_url: str, ruta: str = RUTA_BD) -> bool:
    """Actualiza la URL/ruta de un recurso (RA6: UPDATE parametrizado)."""
    sql = "UPDATE recursos SET url = ? WHERE id = ?"
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute(sql, (nueva_url, id_recurso))
        conn.commit()
        return cursor.rowcount > 0


def eliminar_recurso(id_recurso: int, ruta: str = RUTA_BD) -> bool:
    """Elimina un recurso por su ID."""
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute("DELETE FROM recursos WHERE id = ?", (id_recurso,))
        conn.commit()
        return cursor.rowcount > 0


def eliminar_recursos_antiguos(fecha_limite: str, ruta: str = RUTA_BD) -> int:
    """
    Elimina recursos creados antes de una fecha dada.
    Útil para limpieza de registros antiguos.

    Args:
        fecha_limite: Fecha en formato 'YYYY-MM-DD'.

    Returns:
        Número de registros eliminados.
    """
    sql = "DELETE FROM recursos WHERE fecha_creacion < ?"
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute(sql, (fecha_limite,))
        conn.commit()
        return cursor.rowcount


def insertar_recursos_masivo(lista_recursos: list[tuple], ruta: str = RUTA_BD) -> int:
    """
    Inserta múltiples recursos de una sola vez con executemany (RA6).

    Args:
        lista_recursos: Lista de tuplas (titulo, desc, url, tipo, id_curso, fecha).

    Returns:
        Número de filas insertadas.
    """
    sql = """
        INSERT INTO recursos (titulo, descripcion, url, tipo, id_curso, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    with obtener_conexion(ruta) as conn:
        conn.executemany(sql, lista_recursos)
        conn.commit()
        return len(lista_recursos)


# ═════════════════════════════════════════════════════════════
# RA6 ▶ Operaciones CRUD — USUARIOS
# ═════════════════════════════════════════════════════════════

def insertar_usuario(nombre: str, email: str, rol: str = "estudiante",
                     fecha_registro: str = "", ruta: str = RUTA_BD) -> int:
    """Inserta un usuario con consulta parametrizada."""
    sql = """
        INSERT INTO usuarios (nombre, email, rol, fecha_registro)
        VALUES (?, ?, ?, ?)
    """
    with obtener_conexion(ruta) as conn:
        try:
            cursor = conn.execute(sql, (nombre, email, rol, fecha_registro))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"  ✗ Ya existe un usuario con el email '{email}'.")
            return -1


def consultar_usuarios(ruta: str = RUTA_BD) -> list[dict]:
    """Recupera todos los usuarios de la BD."""
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute("SELECT * FROM usuarios ORDER BY id")
        return [dict(f) for f in cursor.fetchall()]


def eliminar_usuario(id_usuario: int, ruta: str = RUTA_BD) -> bool:
    """Elimina un usuario por su ID."""
    with obtener_conexion(ruta) as conn:
        cursor = conn.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
        conn.commit()
        return cursor.rowcount > 0


# ═════════════════════════════════════════════════════════════
# RA6 ▶ Estadísticas desde BD
# ═════════════════════════════════════════════════════════════

def estadisticas_bd(ruta: str = RUTA_BD) -> dict:
    """
    Genera estadísticas directamente con consultas SQL (GROUP BY).

    Returns:
        Diccionario con conteos y agrupaciones.
    """
    with obtener_conexion(ruta) as conn:
        total_cursos   = conn.execute("SELECT COUNT(*) FROM cursos").fetchone()[0]
        total_recursos = conn.execute("SELECT COUNT(*) FROM recursos").fetchone()[0]
        total_usuarios = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]

        # Recursos agrupados por tipo (GROUP BY)
        sql_tipos = "SELECT tipo, COUNT(*) as cantidad FROM recursos GROUP BY tipo"
        por_tipo = {fila["tipo"]: fila["cantidad"]
                    for fila in conn.execute(sql_tipos).fetchall()}

        # Recursos por curso (JOIN)
        sql_por_curso = """
            SELECT c.titulo, COUNT(r.id) as num_recursos
            FROM cursos c
            LEFT JOIN recursos r ON c.id = r.id_curso
            GROUP BY c.id
            ORDER BY num_recursos DESC
        """
        por_curso = [(f["titulo"], f["num_recursos"])
                     for f in conn.execute(sql_por_curso).fetchall()]

    return {
        "total_cursos": total_cursos,
        "total_recursos": total_recursos,
        "total_usuarios": total_usuarios,
        "recursos_por_tipo": por_tipo,
        "recursos_por_curso": por_curso,
    }


def mostrar_estadisticas_bd(ruta: str = RUTA_BD) -> None:
    """Imprime estadísticas extraídas desde la base de datos."""
    stats = estadisticas_bd(ruta)
    print(f"\n{'═'*55}")
    print(f"  📊  ESTADÍSTICAS DESDE BASE DE DATOS ({ruta})")
    print(f"{'═'*55}")
    print(f"  Cursos    : {stats['total_cursos']}")
    print(f"  Recursos  : {stats['total_recursos']}")
    print(f"  Usuarios  : {stats['total_usuarios']}")
    print(f"\n  Recursos por tipo:")
    for tipo, cantidad in stats["recursos_por_tipo"].items():
        print(f"    {tipo:<10} : {cantidad}")
    print(f"\n  Recursos por curso:")
    for titulo, num in stats["recursos_por_curso"]:
        print(f"    {titulo:<30} : {num}")
    print(f"{'═'*55}")


# ═════════════════════════════════════════════════════════════
# RA6 ▶ Sincronización BD ↔ Plataforma en memoria
# ═════════════════════════════════════════════════════════════

def sincronizar_plataforma_a_bd(plataforma, ruta: str = RUTA_BD) -> None:
    """
    Vuelca el estado actual de la plataforma (en memoria) a la BD.
    Borra todo y reinserta para garantizar consistencia.

    Args:
        plataforma: Instancia de PlataformaEducativa.
        ruta:       Ruta de la base de datos.
    """
    crear_tablas(ruta)
    with obtener_conexion(ruta) as conn:
        # Limpiar tablas sin borrar la estructura
        conn.execute("DELETE FROM recursos")
        conn.execute("DELETE FROM cursos")
        conn.execute("DELETE FROM usuarios")

        # Insertar cursos
        for c in plataforma.cursos:
            conn.execute(
                "INSERT INTO cursos (id, titulo, unidad, descripcion, fecha_creacion) "
                "VALUES (?, ?, ?, ?, ?)",
                (c.id, c.titulo, c.unidad, c.descripcion, c.fecha_creacion)
            )

        # Insertar recursos
        for r in plataforma.recursos:
            conn.execute(
                "INSERT INTO recursos (id, titulo, descripcion, url, tipo, id_curso, fecha_creacion) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (r.id, r.titulo, r.descripcion, r.url, r.tipo, r.id_curso, r.metadatos_fijos[1])
            )

        # Insertar usuarios
        for u in plataforma.usuarios:
            conn.execute(
                "INSERT OR IGNORE INTO usuarios (id, nombre, email, rol, fecha_registro) "
                "VALUES (?, ?, ?, ?, ?)",
                (u.id, u.nombre, u.email, u.rol, u.fecha_registro)
            )

        conn.commit()
    print(f"  ✓ Plataforma sincronizada con la BD '{ruta}'.")
