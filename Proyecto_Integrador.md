# Proyecto Integrador — Plataforma de Gestión Multimedia Educativa

**Asignatura:** Fundamentos de la Programación  
**Versión:** 1.0.0  
**Lenguaje:** Python 3.10+

---

## 1. Descripción general

La **EduMedia Platform** es una aplicación de consola que permite gestionar
cursos, recursos multimedia, usuarios y estadísticas de una plataforma educativa.
Integra los seis Resultados de Aprendizaje (RA) de la asignatura en un único
proyecto cohesionado.

---

## 2. Arquitectura del proyecto

```
FundamentosDeLaProgramacion/
│
├── main.py              ← Menú principal y flujo de la app (RA1, RA2, RA3)
├── modelos.py           ← Clases y herencia OOP (RA4)
├── gestor_archivos.py   ← E/S con TXT, CSV y JSON (RA5)
├── gestor_bd.py         ← SQLite y operaciones CRUD (RA6)
│
├── cursos.txt           ← Datos de cursos en texto plano
├── recursos.csv         ← Exportación de recursos en CSV
├── configuracion.json   ← Configuración de la plataforma
├── preferencias.json    ← Preferencias de usuarios
└── plataforma.db        ← Base de datos SQLite
```

---

## 3. RA1 — Fundamentos y algoritmos

### Algoritmo principal (pseudocódigo)

```
INICIO
  cargar_configuracion()
  crear_tablas_bd()
  crear_plataforma()
  SI usuario quiere demo → cargar_datos_demo()

  MIENTRAS verdadero:
    mostrar_menu_principal()
    opcion ← leer_opcion_usuario()
    SEGÚN opcion:
      0 → guardar_todo(); SALIR
      1 → menu_cursos()
      2 → menu_recursos()
      3 → menu_usuarios()
      4 → menu_estadisticas()
      5 → menu_archivos()
      6 → menu_bd()
FIN
```

### Estructuras de control usadas

| Estructura | Dónde se usa |
|---|---|
| `while True` | Bucle principal del menú y submenús |
| `if / elif / else` | Selección de opciones en cada menú |
| `for` | Iterar listas de cursos, recursos y usuarios |
| `try / except` | Validación de entradas numéricas |
| `break` | Salir de cada submenú con opción `0` |

---

## 4. RA2 — Sintaxis básica de Python

### Variables y tipos usados

| Variable         | Tipo    | Propósito |
|------------------|---------|-----------|
| `titulo`         | `str`   | Nombre de curso o recurso |
| `duracion_seg`   | `float` | Duración de audio/video en segundos |
| `num_paginas`    | `int`   | Páginas de un documento |
| `id`             | `int`   | Identificador único auto-incremental |
| `verificar_acceso()` | `bool` | Permiso de usuario |

### Validación de entradas (funciones en `main.py`)

```python
def leer_entero(mensaje, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"Debe ser >= {minimo}.")
                continue
            return valor
        except ValueError:
            print("Introduce un número entero válido.")
```

- `leer_texto()` — evita campos vacíos
- `leer_float()` — valida decimales con mínimo
- `leer_opcion_menu()` — valida contra un `set` de opciones

---

## 5. RA3 — Colecciones en Python

### Colecciones utilizadas

| Colección| Dónde                             | Para qué                        |
|----------|-----------------------------------|---------------------------------|
| `list` | `plataforma.cursos`, `plataforma.recursos` | Almacén ordenado e iterable|
| `dict` | `to_dict()`, `config`, `conteo_tipo` | Serialización y agrupación       |
| `tuple`| `metadatos_fijos`, `resolucion`   | Datos inmutables (coordenadas, fechas) |
| `set`| `tipos_unicos()`, `ROLES_VALIDOS`, permisos | Eliminar duplicados pertenencia rápida|

### Ejemplos de filtrado y búsqueda

```python
# Filtrar recursos por tipo (list comprehension)
filtrados = [r for r in self.recursos if r.tipo == tipo]

# Buscar cursos por término (list comprehension)
resultado = [c for c in self.cursos
             if termino in c.titulo.lower() or termino in c.unidad.lower()]

# Tipos únicos con set comprehension
tipos = {r.tipo for r in self.recursos}

# Agrupar recursos por unidad con dict
agrupado = {}
for r in self.recursos:
    unidad = curso.unidad
    agrupado.setdefault(unidad, []).append(r)
```

---

## 6. RA4 — Clases, módulos y POO

### Diagrama de clases

```
RecursoMultimedia
├── RecursoTexto       (+num_paginas)
├── RecursoImagen      (+resolucion: tuple)
├── RecursoAudio       (+duracion_seg, +formato)
└── RecursoVideo       (+duracion_seg, +resolucion: tuple)

Curso
└── agrega → RecursoMultimedia (composición)

Usuario
PlataformaEducativa
└── contiene → Curso[], RecursoMultimedia[], Usuario[]
```

### Responsabilidades

| Clase | Responsabilidad |
|-------|-----------------|
| `RecursoMultimedia` | Base con `mostrar_info()` y `to_dict()` polimórficos |
| `RecursoTexto/Imagen/Audio/Video` | Especialización con atributos propios |
| `Curso` | Agrupa recursos, genera estadísticas por tipo |
| `Usuario` | Gestiona rol y verifica permisos de acceso |
| `PlataformaEducativa` | Fachada: orquesta cursos, recursos y usuarios |

### Herencia y polimorfismo

```python
class RecursoAudio(RecursoMultimedia):
    def mostrar_info(self):        # Polimorfismo: override
        super().mostrar_info()     # Reutiliza la implementación base
        print(f"Duración: {self.duracion_seg}s")
```

---

## 7. RA5 — Entrada/Salida con archivos

### Formatos gestionados

| Formato | Archivo | Módulo Python | Uso |
|---|---|---|---|
| TXT | `cursos.txt` | `open()` / `read()` | Resumen legible de cursos |
| CSV | `recursos.csv` | `csv.DictWriter/Reader` | Exportación tabular de recursos |
| JSON | `configuracion.json` | `json.dump/load` | Config y preferencias estructuradas |

### Apertura segura con `with`

```python
# Escritura CSV
with open("recursos.csv", "w", newline="", encoding="utf-8") as f:
    escritor = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
    escritor.writeheader()
    for r in recursos:
        escritor.writerow(r.to_dict())

# Lectura JSON con control de errores
with open("configuracion.json", "r", encoding="utf-8") as f:
    try:
        config = json.load(f)
    except json.JSONDecodeError as e:
        config = CONFIG_DEFECTO.copy()
```

---

## 8. RA6 — Base de datos SQLite

### Esquema de la base de datos

```sql
CREATE TABLE cursos (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT    NOT NULL,
    unidad         TEXT    NOT NULL,
    descripcion    TEXT,
    fecha_creacion TEXT
);

CREATE TABLE recursos (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT    NOT NULL,
    descripcion    TEXT,
    url            TEXT,
    tipo           TEXT    NOT NULL DEFAULT 'generico',
    id_curso       INTEGER NOT NULL,
    fecha_creacion TEXT,
    FOREIGN KEY (id_curso) REFERENCES cursos(id) ON DELETE CASCADE
);

CREATE TABLE usuarios (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         TEXT    NOT NULL,
    email          TEXT    UNIQUE NOT NULL,
    rol            TEXT    NOT NULL DEFAULT 'estudiante',
    fecha_registro TEXT
);
```

### Operaciones CRUD con parámetros

```python
# INSERT parametrizado (evita SQL injection)
conn.execute(
    "INSERT INTO cursos (titulo, unidad, descripcion) VALUES (?, ?, ?)",
    (titulo, unidad, descripcion)
)

# SELECT con filtro
conn.execute("SELECT * FROM recursos WHERE tipo = ?", (tipo,))

# UPDATE
conn.execute("UPDATE recursos SET url = ? WHERE id = ?", (nueva_url, id_r))

# DELETE con CASCADE
conn.execute("DELETE FROM cursos WHERE id = ?", (id_curso,))

# Carga masiva con executemany
conn.executemany(
    "INSERT INTO recursos (...) VALUES (?, ?, ?, ?, ?, ?)",
    lista_de_tuplas
)
```

---

## 9. Ejecución

```bash
python main.py
```

Al iniciar, la aplicación:
1. Carga `configuracion.json` (crea uno por defecto si no existe)
2. Crea/verifica las tablas SQLite en `plataforma.db`
3. Ofrece cargar datos de demostración
4. Presenta el menú principal interactivo

Al salir (opción `0`), guarda automáticamente:
- `cursos.txt`
- `recursos.csv`
- `configuracion.json`
- Sincroniza `plataforma.db`

---

## 10. Posibles mejoras futuras

- Interfaz gráfica con **tkinter**
- API REST básica con **Flask**
- Sistema de autenticación con contraseñas hasheadas (`bcrypt`)
- Exportación a PDF con `reportlab`
- Soporte multiusuario con sesiones
