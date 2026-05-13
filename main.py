"""
main.py
=======
Punto de entrada principal de la Plataforma de Gestión Multimedia Educativa.
Cubre RA1 (algoritmos/flujo), RA2 (sintaxis/validación), RA3 (colecciones).
"""

from modelos import (
    PlataformaEducativa, Curso,
    RecursoTexto, RecursoImagen, RecursoAudio, RecursoVideo,
    Usuario,
)
from gestor_archivos import (
    guardar_cursos_txt, cargar_cursos_txt,
    exportar_recursos_csv, importar_recursos_csv,
    guardar_configuracion_json, cargar_configuracion_json,
    guardar_preferencias_usuario_json, cargar_preferencias_usuario_json,
    explicar_formatos,
)
from gestor_bd import (
    crear_tablas, insertar_curso, insertar_recurso, insertar_usuario,
    consultar_cursos, consultar_recursos, consultar_usuarios,
    actualizar_curso, actualizar_recurso_url,
    eliminar_curso as bd_eliminar_curso,
    eliminar_recurso as bd_eliminar_recurso,
    insertar_recursos_masivo,
    mostrar_estadisticas_bd,
    sincronizar_plataforma_a_bd,
)


# ─────────────────────────────────────────────────────────────
# RA2 ▶ Funciones de validación de entrada
# ─────────────────────────────────────────────────────────────

def leer_entero(mensaje: str, minimo: int = None, maximo: int = None) -> int:
    """Solicita un entero al usuario con validación de rango."""
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  ✗ Debe ser >= {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  ✗ Debe ser <= {maximo}.")
                continue
            return valor
        except ValueError:
            print("  ✗ Introduce un número entero válido.")


def leer_texto(mensaje: str, vacio_ok: bool = False) -> str:
    """Solicita un texto no vacío al usuario."""
    while True:
        valor = input(mensaje).strip()
        if valor or vacio_ok:
            return valor
        print("  ✗ El campo no puede estar vacío.")


def leer_float(mensaje: str, minimo: float = 0.0) -> float:
    """Solicita un número decimal al usuario."""
    while True:
        try:
            valor = float(input(mensaje))
            if valor < minimo:
                print(f"  ✗ Debe ser >= {minimo}.")
                continue
            return valor
        except ValueError:
            print("  ✗ Introduce un número decimal válido.")


def leer_opcion_menu(opciones: set) -> str:
    """Solicita una opción del menú y la valida contra el conjunto de opciones."""
    while True:
        opcion = input("  Opción: ").strip().lower()
        if opcion in opciones:
            return opcion
        print(f"  ✗ Opción no válida. Elige entre: {', '.join(sorted(opciones))}")


# ─────────────────────────────────────────────────────────────
# RA1 ▶ Funciones de menú (flujo / algoritmo principal)
# ─────────────────────────────────────────────────────────────

def imprimir_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          PLATAFORMA DE GESTIÓN MULTIMEDIA EDUCATIVA          ║
╚══════════════════════════════════════════════════════════════╝""")


def menu_principal() -> str:
    print("""
┌─────────────────────────────────────────┐
│            MENÚ PRINCIPAL               │
├─────────────────────────────────────────┤
│  1. Gestión de Cursos                   │
│  2. Gestión de Recursos Multimedia      │
│  3. Gestión de Usuarios                 │
│  4. Estadísticas                        │
│  5. Archivos (TXT / CSV / JSON)         │
│  6. Base de Datos (SQLite)              │
│  7. Información del sistema             │
│  0. Salir                               │
└─────────────────────────────────────────┘""")
    return leer_opcion_menu({"0", "1", "2", "3", "4", "5", "6", "7"})


# ─────────────────────────────────────────────────────────────
# Módulo 1: Cursos
# ─────────────────────────────────────────────────────────────

def menu_cursos(plataforma: PlataformaEducativa):
    while True:
        print("""
  ┌── CURSOS ──────────────────────────────┐
  │  1. Añadir curso                        │
  │  2. Listar cursos                       │
  │  3. Buscar curso                        │
  │  4. Ver recursos de un curso            │
  │  5. Eliminar curso                      │
  │  0. Volver                              │
  └─────────────────────────────────────────┘""")
        op = leer_opcion_menu({"0", "1", "2", "3", "4", "5"})

        if op == "0":
            break
        elif op == "1":
            titulo = leer_texto("  Título del curso: ")
            unidad = leer_texto("  Unidad formativa: ")
            desc   = leer_texto("  Descripción: ", vacio_ok=True)
            curso  = plataforma.agregar_curso(titulo, unidad, desc)
            print(f"  ✓ Curso '{curso.titulo}' creado con ID {curso.id}.")
        elif op == "2":
            plataforma.listar_cursos()
        elif op == "3":
            termino   = leer_texto("  Término de búsqueda: ")
            resultado = plataforma.buscar_curso(termino)
            if resultado:
                for c in resultado:
                    print(f"  → {c}")
            else:
                print("  No se encontraron cursos.")
        elif op == "4":
            plataforma.listar_cursos()
            id_c = leer_entero("  ID del curso: ", minimo=1)
            curso = plataforma.obtener_curso_por_id(id_c)
            if curso:
                print(f"\n  Recursos del curso '{curso.titulo}':")
                curso.listar_recursos()
            else:
                print("  ✗ Curso no encontrado.")
        elif op == "5":
            plataforma.listar_cursos()
            id_c = leer_entero("  ID del curso a eliminar: ", minimo=1)
            if plataforma.eliminar_curso(id_c):
                print("  ✓ Curso eliminado.")
            else:
                print("  ✗ Curso no encontrado.")


# ─────────────────────────────────────────────────────────────
# Módulo 2: Recursos Multimedia
# ─────────────────────────────────────────────────────────────

def pedir_recurso_base() -> tuple:
    """Pide campos comunes a cualquier recurso. Devuelve (titulo, desc, url)."""
    titulo = leer_texto("  Título del recurso: ")
    desc   = leer_texto("  Descripción: ", vacio_ok=True)
    url    = leer_texto("  URL o ruta del archivo: ", vacio_ok=True)
    return titulo, desc, url


def crear_recurso_interactivo(plataforma: PlataformaEducativa):
    """Crea un recurso del tipo seleccionado por el usuario."""
    if not plataforma.cursos:
        print("  ✗ No hay cursos. Añade un curso primero.")
        return

    plataforma.listar_cursos()
    id_c = leer_entero("  ID del curso al que asociar el recurso: ", minimo=1)
    if not plataforma.obtener_curso_por_id(id_c):
        print("  ✗ Curso no encontrado.")
        return

    print("  Tipo: 1) Texto  2) Imagen  3) Audio  4) Vídeo")
    tipo_op = leer_opcion_menu({"1", "2", "3", "4"})
    titulo, desc, url = pedir_recurso_base()

    if tipo_op == "1":
        paginas = leer_entero("  Número de páginas: ", minimo=0)
        recurso = RecursoTexto(titulo, desc, url, id_c, paginas)
    elif tipo_op == "2":
        ancho = leer_entero("  Ancho (px): ", minimo=0)
        alto  = leer_entero("  Alto (px): ", minimo=0)
        recurso = RecursoImagen(titulo, desc, url, id_c, (ancho, alto))
    elif tipo_op == "3":
        dur    = leer_float("  Duración (segundos): ")
        fmt    = leer_texto("  Formato (mp3/ogg/wav): ", vacio_ok=True) or "mp3"
        recurso = RecursoAudio(titulo, desc, url, id_c, dur, fmt)
    else:
        dur   = leer_float("  Duración (segundos): ")
        ancho = leer_entero("  Ancho resolución (px): ", minimo=0)
        alto  = leer_entero("  Alto resolución (px): ", minimo=0)
        recurso = RecursoVideo(titulo, desc, url, id_c, dur, (ancho, alto))

    plataforma.agregar_recurso(recurso, id_c)
    print(f"  ✓ Recurso '{recurso.titulo}' añadido (ID {recurso.id}).")


def menu_recursos(plataforma: PlataformaEducativa):
    # RA3: set de tipos disponibles
    TIPOS: set = {"texto", "imagen", "audio", "video"}

    while True:
        print("""
  ┌── RECURSOS MULTIMEDIA ─────────────────┐
  │  1. Añadir recurso                      │
  │  2. Listar todos los recursos           │
  │  3. Listar por tipo                     │
  │  4. Buscar recurso                      │
  │  5. Ver detalle de un recurso           │
  │  6. Exportar a CSV                      │
  │  0. Volver                              │
  └─────────────────────────────────────────┘""")
        op = leer_opcion_menu({"0", "1", "2", "3", "4", "5", "6"})

        if op == "0":
            break
        elif op == "1":
            crear_recurso_interactivo(plataforma)
        elif op == "2":
            plataforma.listar_recursos()
        elif op == "3":
            print(f"  Tipos disponibles: {', '.join(TIPOS)}")
            tipo = leer_texto("  Tipo: ").lower()
            if tipo not in TIPOS:
                print("  ✗ Tipo no válido.")
            else:
                plataforma.listar_recursos(tipo)
        elif op == "4":
            termino = leer_texto("  Término de búsqueda: ")
            resultados = plataforma.buscar_recurso(termino)
            if resultados:
                for r in resultados:
                    print(f"  → {r}")
            else:
                print("  Sin resultados.")
        elif op == "5":
            plataforma.listar_recursos()
            id_r = leer_entero("  ID del recurso: ", minimo=1)
            recurso = next((r for r in plataforma.recursos if r.id == id_r), None)
            if recurso:
                print()
                recurso.mostrar_info()
            else:
                print("  ✗ Recurso no encontrado.")
        elif op == "6":
            exportar_recursos_csv(plataforma.recursos)


# ─────────────────────────────────────────────────────────────
# Módulo 3: Usuarios
# ─────────────────────────────────────────────────────────────

def menu_usuarios(plataforma: PlataformaEducativa):
    ROLES_VALIDOS: set = {"admin", "docente", "estudiante"}  # RA3: set

    while True:
        print("""
  ┌── USUARIOS ────────────────────────────┐
  │  1. Registrar usuario                   │
  │  2. Listar usuarios                     │
  │  3. Ver permisos de un usuario          │
  │  4. Guardar preferencias (JSON)         │
  │  5. Cargar preferencias (JSON)          │
  │  0. Volver                              │
  └─────────────────────────────────────────┘""")
        op = leer_opcion_menu({"0", "1", "2", "3", "4", "5"})

        if op == "0":
            break
        elif op == "1":
            nombre = leer_texto("  Nombre: ")
            email  = leer_texto("  Email: ")
            print(f"  Roles disponibles: {', '.join(ROLES_VALIDOS)}")
            rol = leer_texto("  Rol: ").lower()
            if rol not in ROLES_VALIDOS:
                print(f"  ⚠ Rol no reconocido. Se asignará 'estudiante'.")
                rol = "estudiante"
            usuario = plataforma.registrar_usuario(nombre, email, rol)
            print(f"  ✓ Usuario '{usuario.nombre}' registrado con ID {usuario.id}.")
        elif op == "2":
            plataforma.listar_usuarios()
        elif op == "3":
            plataforma.listar_usuarios()
            id_u = leer_entero("  ID del usuario: ", minimo=1)
            usuario = plataforma.obtener_usuario_por_id(id_u)
            if usuario:
                acciones = ["ver", "crear", "editar", "eliminar", "exportar"]
                print(f"\n  Permisos de '{usuario.nombre}' [{usuario.rol}]:")
                for acc in acciones:
                    permiso = "✓" if usuario.verificar_acceso(acc) else "✗"
                    print(f"    {permiso} {acc}")
            else:
                print("  ✗ Usuario no encontrado.")
        elif op == "4":
            plataforma.listar_usuarios()
            id_u = leer_entero("  ID del usuario: ", minimo=1)
            usuario = plataforma.obtener_usuario_por_id(id_u)
            if usuario:
                clave = leer_texto("  Clave de preferencia: ")
                valor = leer_texto("  Valor: ")
                usuario.guardar_preferencia(clave, valor)
                guardar_preferencias_usuario_json(usuario.id, usuario.preferencias)
            else:
                print("  ✗ Usuario no encontrado.")
        elif op == "5":
            id_u = leer_entero("  ID del usuario: ", minimo=1)
            prefs = cargar_preferencias_usuario_json(id_u)
            if prefs:
                print(f"  Preferencias del usuario {id_u}:")
                for k, v in prefs.items():
                    print(f"    {k}: {v}")
            else:
                print("  Sin preferencias guardadas.")


# ─────────────────────────────────────────────────────────────
# Módulo 4: Estadísticas
# ─────────────────────────────────────────────────────────────

def menu_estadisticas(plataforma: PlataformaEducativa):
    while True:
        print("""
  ┌── ESTADÍSTICAS ────────────────────────┐
  │  1. Estadísticas generales (memoria)   │
  │  2. Estadísticas desde BD (SQLite)     │
  │  3. Tipos únicos de recursos           │
  │  4. Recursos agrupados por unidad      │
  │  0. Volver                             │
  └─────────────────────────────────────────┘""")
        op = leer_opcion_menu({"0", "1", "2", "3", "4"})

        if op == "0":
            break
        elif op == "1":
            plataforma.mostrar_estadisticas()
        elif op == "2":
            mostrar_estadisticas_bd()
        elif op == "3":
            # RA3: operación sobre sets
            tipos = plataforma.tipos_unicos()
            print(f"\n  Tipos de recursos registrados: {tipos if tipos else '(ninguno)'}")
        elif op == "4":
            agrupado = plataforma.recursos_por_unidad()
            if not agrupado:
                print("  Sin datos.")
            else:
                for unidad, recursos in agrupado.items():
                    print(f"\n  [{unidad}] — {len(recursos)} recurso(s):")
                    for r in recursos:
                        print(f"    • [{r.tipo}] {r.titulo}")


# ─────────────────────────────────────────────────────────────
# Módulo 5: Archivos
# ─────────────────────────────────────────────────────────────

def menu_archivos(plataforma: PlataformaEducativa, config: dict):
    while True:
        print("""
  ┌── ARCHIVOS ────────────────────────────┐
  │  1. Guardar cursos en TXT              │
  │  2. Leer cursos desde TXT              │
  │  3. Exportar recursos a CSV            │
  │  4. Importar recursos desde CSV        │
  │  5. Guardar configuración (JSON)       │
  │  6. Cargar configuración (JSON)        │
  │  7. Ver diferencias entre formatos     │
  │  0. Volver                             │
  └─────────────────────────────────────────┘""")
        op = leer_opcion_menu({"0", "1", "2", "3", "4", "5", "6", "7"})

        if op == "0":
            break
        elif op == "1":
            guardar_cursos_txt(plataforma.cursos)
        elif op == "2":
            datos = cargar_cursos_txt()
            if datos:
                print(f"  Cursos leídos del TXT ({len(datos)}):")
                for d in datos:
                    print(f"    ID:{d.get('id','?')} | {d.get('título','?')} | {d.get('unidad','?')}")
        elif op == "3":
            exportar_recursos_csv(plataforma.recursos)
        elif op == "4":
            filas = importar_recursos_csv()
            if filas:
                print(f"  Primera fila importada: {filas[0]}")
        elif op == "5":
            guardar_configuracion_json(config)
        elif op == "6":
            config.update(cargar_configuracion_json())
            print(f"  Config cargada: {config}")
        elif op == "7":
            explicar_formatos()


# ─────────────────────────────────────────────────────────────
# Módulo 6: Base de Datos
# ─────────────────────────────────────────────────────────────

def menu_bd(plataforma: PlataformaEducativa):
    while True:
        print("""
  ┌── BASE DE DATOS (SQLite) ──────────────┐
  │  1. Crear/verificar tablas             │
  │  2. Sincronizar plataforma → BD        │
  │  3. Listar cursos desde BD             │
  │  4. Listar recursos desde BD           │
  │  5. Listar usuarios desde BD           │
  │  6. Actualizar URL de recurso (BD)     │
  │  7. Eliminar curso de BD               │
  │  8. Carga masiva de recursos (demo)    │
  │  9. Estadísticas desde BD              │
  │  0. Volver                             │
  └─────────────────────────────────────────┘""")
        op = leer_opcion_menu({"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"})

        if op == "0":
            break
        elif op == "1":
            crear_tablas()
        elif op == "2":
            sincronizar_plataforma_a_bd(plataforma)
        elif op == "3":
            filas = consultar_cursos()
            if filas:
                print(f"\n  {'ID':<5} {'Título':<25} {'Unidad'}")
                print("  " + "─" * 50)
                for f in filas:
                    print(f"  {f['id']:<5} {f['titulo']:<25} {f['unidad']}")
            else:
                print("  (Sin cursos en BD)")
        elif op == "4":
            filas = consultar_recursos()
            if filas:
                print(f"\n  {'ID':<5} {'Tipo':<10} {'Título':<25} {'Curso'}")
                print("  " + "─" * 55)
                for f in filas:
                    print(f"  {f['id']:<5} {f['tipo']:<10} {f['titulo']:<25} {f['id_curso']}")
            else:
                print("  (Sin recursos en BD)")
        elif op == "5":
            filas = consultar_usuarios()
            for f in filas:
                print(f"  {f['id']:<5} {f['nombre']:<20} {f['rol']}")
        elif op == "6":
            id_r    = leer_entero("  ID del recurso: ", minimo=1)
            nueva   = leer_texto("  Nueva URL: ")
            ok = actualizar_recurso_url(id_r, nueva)
            print("  ✓ Actualizado." if ok else "  ✗ No encontrado.")
        elif op == "7":
            id_c = leer_entero("  ID del curso a eliminar: ", minimo=1)
            ok = bd_eliminar_curso(id_c)
            print("  ✓ Curso eliminado de BD." if ok else "  ✗ No encontrado.")
        elif op == "8":
            from datetime import datetime
            hoy = datetime.now().strftime("%Y-%m-%d")
            demo_data = [
                ("Demo Audio 1", "Audio demo", "audio1.mp3", "audio", 1, hoy),
                ("Demo Video 1", "Video demo", "video1.mp4", "video", 1, hoy),
                ("Demo Texto 1", "Texto demo", "doc1.pdf",   "texto", 1, hoy),
            ]
            n = insertar_recursos_masivo(demo_data)
            print(f"  ✓ {n} recursos insertados masivamente.")
        elif op == "9":
            mostrar_estadisticas_bd()


# ─────────────────────────────────────────────────────────────
# RA4 ▶ Datos de demo para iniciar con contenido
# ─────────────────────────────────────────────────────────────

def cargar_datos_demo(plataforma: PlataformaEducativa) -> None:
    """Puebla la plataforma con datos de ejemplo para demostración."""
    c1 = plataforma.agregar_curso(
        "Introducción a Python", "Unidad 1",
        "Fundamentos básicos del lenguaje Python")
    c2 = plataforma.agregar_curso(
        "Bases de Datos con SQLite", "Unidad 2",
        "Acceso y gestión de datos relacionales")
    c3 = plataforma.agregar_curso(
        "Diseño Web Básico", "Unidad 3",
        "HTML, CSS y publicación de páginas")

    plataforma.agregar_recurso(RecursoTexto("Manual Python", "Guía completa", "python.pdf", c1.id, 120), c1.id)
    plataforma.agregar_recurso(RecursoVideo("Clase 1 - Variables", "Primera clase", "clase1.mp4", c1.id, 3600, (1920, 1080)), c1.id)
    plataforma.agregar_recurso(RecursoAudio("Podcast Python", "Episodio intro", "podcast.mp3", c1.id, 1800, "mp3"), c1.id)

    plataforma.agregar_recurso(RecursoTexto("Guía SQLite", "Referencia SQLite3", "sqlite.pdf", c2.id, 80), c2.id)
    plataforma.agregar_recurso(RecursoVideo("Demo SQL", "Consultas en vivo", "demo_sql.mp4", c2.id, 2700, (1280, 720)), c2.id)
    plataforma.agregar_recurso(RecursoImagen("Diagrama ER", "Modelo entidad-relación", "er.png", c2.id, (1920, 1080)), c2.id)

    plataforma.agregar_recurso(RecursoTexto("HTML Cheatsheet", "Referencia rápida HTML", "html.pdf", c3.id, 10), c3.id)
    plataforma.agregar_recurso(RecursoImagen("Wireframe Web", "Diseño inicial", "wireframe.jpg", c3.id, (800, 600)), c3.id)

    plataforma.registrar_usuario("Ana García",    "ana@edu.es",    "admin")
    plataforma.registrar_usuario("Carlos López",  "carlos@edu.es", "docente")
    plataforma.registrar_usuario("María Martínez","maria@edu.es",  "estudiante")

    print("  ✓ Datos de demostración cargados.")


# ─────────────────────────────────────────────────────────────
# RA1 ▶ Algoritmo principal (bucle principal de la aplicación)
# ─────────────────────────────────────────────────────────────

def main():
    """
    Algoritmo principal de la plataforma:
    1. Iniciar aplicación y cargar configuración
    2. Mostrar menú principal
    3. Recibir opción del usuario
    4. Ejecutar acción seleccionada
    5. Repetir hasta que el usuario elija salir (opción 0)
    """
    imprimir_banner()

    # Paso 1: Inicializar
    config = cargar_configuracion_json()
    crear_tablas()

    nombre_plataforma = config.get("nombre_plataforma", "EduMedia Platform")
    plataforma = PlataformaEducativa(nombre_plataforma)

    print(f"\n  Bienvenido/a a {plataforma.nombre}")
    cargar = input("  ¿Cargar datos de demostración? (s/n): ").strip().lower()
    if cargar == "s":
        cargar_datos_demo(plataforma)

    # Paso 2-5: Bucle principal (RA1)
    while True:
        opcion = menu_principal()  # Paso 2 y 3

        # Paso 4: Ejecutar acción
        if opcion == "0":
            # Guardar antes de salir
            print("\n  Guardando datos antes de salir...")
            guardar_cursos_txt(plataforma.cursos)
            exportar_recursos_csv(plataforma.recursos)
            guardar_configuracion_json(config)
            sincronizar_plataforma_a_bd(plataforma)
            print("\n  ¡Hasta pronto! 👋")
            break
        elif opcion == "1":
            menu_cursos(plataforma)
        elif opcion == "2":
            menu_recursos(plataforma)
        elif opcion == "3":
            menu_usuarios(plataforma)
        elif opcion == "4":
            menu_estadisticas(plataforma)
        elif opcion == "5":
            menu_archivos(plataforma, config)
        elif opcion == "6":
            menu_bd(plataforma)
        elif opcion == "7":
            print(f"\n  {plataforma}")
            print(f"  Config: {config}")


if __name__ == "__main__":
    main()
