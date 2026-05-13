"""
modelos.py
==========
Módulo de modelos y clases principales de la plataforma educativa.
Cubre el RA4: Programación Orientada a Objetos, herencia y módulos.

Clases:
    - RecursoMultimedia (base)
        - RecursoTexto
        - RecursoImagen
        - RecursoAudio
        - RecursoVideo
    - Curso
    - Usuario
    - PlataformaEducativa
"""

from datetime import datetime


# ─────────────────────────────────────────────────────────────
# RA4 ▶ Jerarquía de RecursoMultimedia (herencia / polimorfismo)
# ─────────────────────────────────────────────────────────────

class RecursoMultimedia:
    """Clase base para cualquier recurso multimedia de la plataforma."""

    # Contador de clase para asignar IDs automáticos
    _contador: int = 0

    def __init__(self, titulo: str, descripcion: str, url: str, id_curso: int):
        RecursoMultimedia._contador += 1
        self.id: int = RecursoMultimedia._contador
        self.titulo: str = titulo
        self.descripcion: str = descripcion
        self.url: str = url
        self.id_curso: int = id_curso
        self.tipo: str = "generico"
        # Tupla inmutable de metadatos fijos (RA3: uso de tuplas)
        self.metadatos_fijos: tuple = (self.id, datetime.now().strftime("%Y-%m-%d"))

    def mostrar_info(self) -> None:
        """Muestra información básica del recurso. Polimorfismo → cada subclase lo enriquece."""
        print(f"  [{self.tipo.upper()}] ID:{self.id} | {self.titulo}")
        print(f"    Descripción : {self.descripcion}")
        print(f"    URL/Ruta    : {self.url}")
        print(f"    Curso ID    : {self.id_curso}")
        print(f"    Creado      : {self.metadatos_fijos[1]}")

    def to_dict(self) -> dict:
        """Serializa el recurso a diccionario (RA3: diccionarios)."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "url": self.url,
            "id_curso": self.id_curso,
            "tipo": self.tipo,
            "fecha_creacion": self.metadatos_fijos[1],
        }

    def __str__(self) -> str:
        return f"[{self.tipo.upper()}] {self.titulo} (Curso {self.id_curso})"

    def __repr__(self) -> str:
        return f"RecursoMultimedia(id={self.id}, tipo={self.tipo!r}, titulo={self.titulo!r})"


class RecursoTexto(RecursoMultimedia):
    """Recurso de tipo texto o documento."""

    def __init__(self, titulo: str, descripcion: str, url: str, id_curso: int, num_paginas: int = 0):
        super().__init__(titulo, descripcion, url, id_curso)
        self.tipo = "texto"
        self.num_paginas: int = num_paginas

    def mostrar_info(self) -> None:
        super().mostrar_info()
        print(f"    Páginas     : {self.num_paginas}")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["num_paginas"] = self.num_paginas
        return d


class RecursoImagen(RecursoMultimedia):
    """Recurso de tipo imagen."""

    def __init__(self, titulo: str, descripcion: str, url: str, id_curso: int,
                 resolucion: tuple = (0, 0)):
        super().__init__(titulo, descripcion, url, id_curso)
        self.tipo = "imagen"
        # Tupla inmutable: ancho x alto (RA3: tuplas para datos fijos)
        self.resolucion: tuple = resolucion

    def mostrar_info(self) -> None:
        super().mostrar_info()
        print(f"    Resolución  : {self.resolucion[0]}x{self.resolucion[1]} px")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["resolucion"] = f"{self.resolucion[0]}x{self.resolucion[1]}"
        return d


class RecursoAudio(RecursoMultimedia):
    """Recurso de tipo audio."""

    def __init__(self, titulo: str, descripcion: str, url: str, id_curso: int,
                 duracion_seg: float = 0.0, formato: str = "mp3"):
        super().__init__(titulo, descripcion, url, id_curso)
        self.tipo = "audio"
        self.duracion_seg: float = duracion_seg
        self.formato: str = formato

    def mostrar_info(self) -> None:
        super().mostrar_info()
        minutos, segundos = divmod(int(self.duracion_seg), 60)
        print(f"    Duración    : {minutos}m {segundos}s  |  Formato: {self.formato}")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["duracion_seg"] = self.duracion_seg
        d["formato"] = self.formato
        return d


class RecursoVideo(RecursoMultimedia):
    """Recurso de tipo vídeo."""

    def __init__(self, titulo: str, descripcion: str, url: str, id_curso: int,
                 duracion_seg: float = 0.0, resolucion: tuple = (1920, 1080)):
        super().__init__(titulo, descripcion, url, id_curso)
        self.tipo = "video"
        self.duracion_seg: float = duracion_seg
        # Tupla inmutable (RA3)
        self.resolucion: tuple = resolucion

    def mostrar_info(self) -> None:
        super().mostrar_info()
        minutos, segundos = divmod(int(self.duracion_seg), 60)
        print(f"    Duración    : {minutos}m {segundos}s")
        print(f"    Resolución  : {self.resolucion[0]}x{self.resolucion[1]} px")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["duracion_seg"] = self.duracion_seg
        d["resolucion"] = f"{self.resolucion[0]}x{self.resolucion[1]}"
        return d


# ─────────────────────────────────────────────────────────────
# RA4 ▶ Clase Curso
# ─────────────────────────────────────────────────────────────

class Curso:
    """Representa un curso o módulo formativo de la plataforma."""

    _contador: int = 0

    def __init__(self, titulo: str, unidad: str, descripcion: str):
        Curso._contador += 1
        self.id: int = Curso._contador
        self.titulo: str = titulo
        self.unidad: str = unidad
        self.descripcion: str = descripcion
        # Lista de objetos RecursoMultimedia asociados (RA3: listas)
        self.recursos: list[RecursoMultimedia] = []
        self.fecha_creacion: str = datetime.now().strftime("%Y-%m-%d")

    def agregar_recurso(self, recurso: RecursoMultimedia) -> None:
        """Asocia un recurso multimedia al curso."""
        recurso.id_curso = self.id
        self.recursos.append(recurso)
        print(f"  ✓ Recurso '{recurso.titulo}' añadido al curso '{self.titulo}'.")

    def listar_recursos(self) -> None:
        """Muestra todos los recursos del curso."""
        if not self.recursos:
            print("  (Sin recursos registrados)")
            return
        for r in self.recursos:
            print(f"    • [{r.tipo.upper()}] {r.titulo}")

    def contar_por_tipo(self) -> dict:
        """Devuelve un diccionario con el conteo de recursos por tipo (RA3)."""
        conteo: dict = {}
        for r in self.recursos:
            conteo[r.tipo] = conteo.get(r.tipo, 0) + 1
        return conteo

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "unidad": self.unidad,
            "descripcion": self.descripcion,
            "fecha_creacion": self.fecha_creacion,
            "num_recursos": len(self.recursos),
        }

    def __str__(self) -> str:
        return f"Curso #{self.id}: {self.titulo} | Unidad: {self.unidad}"

    def __repr__(self) -> str:
        return f"Curso(id={self.id}, titulo={self.titulo!r})"


# ─────────────────────────────────────────────────────────────
# RA4 ▶ Clase Usuario
# ─────────────────────────────────────────────────────────────

class Usuario:
    """Representa a un usuario registrado en la plataforma."""

    _contador: int = 0
    _ROLES_VALIDOS: set = {"admin", "docente", "estudiante"}   # RA3: sets

    def __init__(self, nombre: str, email: str, rol: str = "estudiante"):
        Usuario._contador += 1
        self.id: int = Usuario._contador
        self.nombre: str = nombre
        self.email: str = email
        # Validación de rol usando set (RA3)
        self.rol: str = rol if rol in Usuario._ROLES_VALIDOS else "estudiante"
        self.fecha_registro: str = datetime.now().strftime("%Y-%m-%d")
        self.preferencias: dict = {}   # Guardado en JSON (RA5)

    def verificar_acceso(self, accion: str) -> bool:
        """Comprueba si el usuario puede realizar una acción según su rol."""
        permisos: dict = {
            "admin": {"ver", "crear", "editar", "eliminar", "exportar"},
            "docente": {"ver", "crear", "editar", "exportar"},
            "estudiante": {"ver"},
        }
        return accion in permisos.get(self.rol, set())

    def guardar_preferencia(self, clave: str, valor) -> None:
        """Guarda una preferencia del usuario (luego persistida en JSON)."""
        self.preferencias[clave] = valor

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "fecha_registro": self.fecha_registro,
        }

    def __str__(self) -> str:
        return f"Usuario #{self.id}: {self.nombre} <{self.email}> [{self.rol}]"

    def __repr__(self) -> str:
        return f"Usuario(id={self.id}, nombre={self.nombre!r}, rol={self.rol!r})"


# ─────────────────────────────────────────────────────────────
# RA4 ▶ Clase PlataformaEducativa (fachada principal)
# ─────────────────────────────────────────────────────────────

class PlataformaEducativa:
    """
    Clase principal que orquesta cursos, recursos y usuarios.
    Actúa como fachada (Facade) para toda la lógica de negocio.
    """

    def __init__(self, nombre: str = "EduMedia Platform"):
        self.nombre: str = nombre
        # RA3: listas de instancias
        self.cursos: list[Curso] = []
        self.recursos: list[RecursoMultimedia] = []
        self.usuarios: list[Usuario] = []
        # RA3: set de géneros/etiquetas únicas
        self.etiquetas: set = set()

    # ── Gestión de cursos ──────────────────────────────────────

    def agregar_curso(self, titulo: str, unidad: str, descripcion: str) -> Curso:
        curso = Curso(titulo, unidad, descripcion)
        self.cursos.append(curso)
        return curso

    def listar_cursos(self) -> None:
        if not self.cursos:
            print("  No hay cursos registrados.")
            return
        print(f"\n{'─'*60}")
        print(f"  {'ID':<5} {'Título':<25} {'Unidad':<15} {'Recursos'}")
        print(f"{'─'*60}")
        for c in self.cursos:
            print(f"  {c.id:<5} {c.titulo:<25} {c.unidad:<15} {len(c.recursos)}")
        print(f"{'─'*60}")

    def buscar_curso(self, termino: str) -> list[Curso]:
        """Busca cursos por título o unidad (RA3: filtros sobre listas)."""
        termino = termino.lower()
        return [c for c in self.cursos
                if termino in c.titulo.lower() or termino in c.unidad.lower()]

    def obtener_curso_por_id(self, id_curso: int) -> Curso | None:
        for c in self.cursos:
            if c.id == id_curso:
                return c
        return None

    def eliminar_curso(self, id_curso: int) -> bool:
        curso = self.obtener_curso_por_id(id_curso)
        if curso:
            self.cursos.remove(curso)
            # Eliminar también sus recursos de la lista global
            self.recursos = [r for r in self.recursos if r.id_curso != id_curso]
            return True
        return False

    # ── Gestión de recursos ───────────────────────────────────

    def agregar_recurso(self, recurso: RecursoMultimedia, id_curso: int) -> bool:
        curso = self.obtener_curso_por_id(id_curso)
        if not curso:
            return False
        curso.agregar_recurso(recurso)
        self.recursos.append(recurso)
        return True

    def listar_recursos(self, tipo: str | None = None) -> None:
        """Lista recursos, opcionalmente filtrados por tipo (RA3)."""
        filtrados = self.recursos if tipo is None else [r for r in self.recursos if r.tipo == tipo]
        if not filtrados:
            print("  No se encontraron recursos.")
            return
        print(f"\n{'─'*70}")
        for r in filtrados:
            print(f"  ID:{r.id:<4} [{r.tipo.upper():<7}] {r.titulo:<30} Curso:{r.id_curso}")
        print(f"{'─'*70}")

    def buscar_recurso(self, termino: str) -> list[RecursoMultimedia]:
        """Busca recursos por título o descripción."""
        termino = termino.lower()
        return [r for r in self.recursos
                if termino in r.titulo.lower() or termino in r.descripcion.lower()]

    def recursos_por_unidad(self) -> dict:
        """Agrupa recursos según la unidad de su curso (RA3: dict)."""
        agrupado: dict = {}
        for r in self.recursos:
            curso = self.obtener_curso_por_id(r.id_curso)
            unidad = curso.unidad if curso else "Sin unidad"
            agrupado.setdefault(unidad, []).append(r)
        return agrupado

    def tipos_unicos(self) -> set:
        """Devuelve el conjunto de tipos de recursos registrados (RA3: sets)."""
        return {r.tipo for r in self.recursos}

    # ── Gestión de usuarios ────────────────────────────────────

    def registrar_usuario(self, nombre: str, email: str, rol: str = "estudiante") -> Usuario:
        usuario = Usuario(nombre, email, rol)
        self.usuarios.append(usuario)
        return usuario

    def obtener_usuario_por_id(self, id_usuario: int) -> Usuario | None:
        for u in self.usuarios:
            if u.id == id_usuario:
                return u
        return None

    def listar_usuarios(self) -> None:
        if not self.usuarios:
            print("  No hay usuarios registrados.")
            return
        print(f"\n{'─'*65}")
        print(f"  {'ID':<5} {'Nombre':<20} {'Email':<25} {'Rol'}")
        print(f"{'─'*65}")
        for u in self.usuarios:
            print(f"  {u.id:<5} {u.nombre:<20} {u.email:<25} {u.rol}")
        print(f"{'─'*65}")

    # ── Estadísticas ──────────────────────────────────────────

    def estadisticas(self) -> dict:
        """Genera estadísticas generales de la plataforma."""
        total_recursos = len(self.recursos)
        conteo_tipo: dict = {}
        for r in self.recursos:
            conteo_tipo[r.tipo] = conteo_tipo.get(r.tipo, 0) + 1

        porcentajes: dict = {}
        if total_recursos > 0:
            for tipo, cantidad in conteo_tipo.items():
                porcentajes[tipo] = round((cantidad / total_recursos) * 100, 2)

        return {
            "total_cursos": len(self.cursos),
            "total_recursos": total_recursos,
            "total_usuarios": len(self.usuarios),
            "recursos_por_tipo": conteo_tipo,
            "porcentaje_por_tipo": porcentajes,
        }

    def mostrar_estadisticas(self) -> None:
        stats = self.estadisticas()
        print(f"\n{'═'*50}")
        print(f"  📊 ESTADÍSTICAS DE {self.nombre.upper()}")
        print(f"{'═'*50}")
        print(f"  Cursos registrados   : {stats['total_cursos']}")
        print(f"  Recursos totales     : {stats['total_recursos']}")
        print(f"  Usuarios registrados : {stats['total_usuarios']}")
        print(f"\n  Recursos por tipo:")
        for tipo, cant in stats["recursos_por_tipo"].items():
            pct = stats["porcentaje_por_tipo"].get(tipo, 0)
            barra = "█" * int(pct // 5)
            print(f"    {tipo:<10} : {cant:>3}  ({pct:>6.2f}%)  {barra}")
        print(f"{'═'*50}")

    def __str__(self) -> str:
        return (f"{self.nombre} | "
                f"Cursos: {len(self.cursos)} | "
                f"Recursos: {len(self.recursos)} | "
                f"Usuarios: {len(self.usuarios)}")
