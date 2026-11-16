import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

ARCHIVO = Path(__file__).parent / "datos" / "libros.json"
CAMPOS = {"id", "titulo", "autor", "anio", "disponible"}

libros = []
contador_id = 1


def cargar():
    global contador_id
    libros.clear()
    contador_id = 1
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            datos = json.load(f)
        if not isinstance(datos, list):
            return
        for d in datos:
            if not isinstance(d, dict) or not CAMPOS <= d.keys() or not isinstance(d["id"], int):
                return
        libros.extend(datos)
        libros.sort(key=lambda l: l["id"])
        if libros:
            contador_id = max(l["id"] for l in libros) + 1
    except (OSError, ValueError):
        pass


def guardar():
    ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(libros, f, ensure_ascii=False, indent=2)


cargar()


class LibroEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=60)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True


class LibroParcial(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=100)
    autor: str | None = Field(default=None, min_length=3, max_length=60)
    anio: int | None = Field(default=None, ge=1000, le=2100)
    disponible: bool | None = None


class Libro(LibroEntrada):
    id: int


def buscar_libro(libro_id: int):
    for libro in libros:
        if libro["id"] == libro_id:
            return libro
    return None


@app.get("/")
def raiz():
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros")
def listar_libros(
    autor: str | None = None,
    disponible: bool | None = None,
    desde: int = 0,
    limite: int = 100,
):
    resultado = libros
    if autor is not None:
        resultado = [l for l in resultado if l["autor"].lower() == autor.lower()]
    if disponible is not None:
        resultado = [l for l in resultado if l["disponible"] == disponible]
    return resultado[desde : desde + limite]


@app.post("/libros", status_code=201, response_model=Libro)
def crear_libro(datos: LibroEntrada):
    global contador_id
    for existente in libros:
        if (
            existente["titulo"].lower() == datos.titulo.lower()
            and existente["autor"].lower() == datos.autor.lower()
        ):
            raise HTTPException(status_code=409, detail="El libro ya existe")
    libro = {"id": contador_id, **datos.model_dump()}
    contador_id += 1
    libros.append(libro)
    guardar()
    return libro


@app.get("/libros/{libro_id}", response_model=Libro)
def obtener_libro(libro_id: int):
    libro = buscar_libro(libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro


@app.put("/libros/{libro_id}", response_model=Libro)
def reemplazar_libro(libro_id: int, datos: LibroEntrada):
    libro = buscar_libro(libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    libro.update(datos.model_dump())
    guardar()
    return libro


@app.patch("/libros/{libro_id}", response_model=Libro)
def actualizar_libro(libro_id: int, datos: LibroParcial):
    libro = buscar_libro(libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    libro.update(datos.model_dump(exclude_unset=True))
    guardar()
    return libro


@app.delete("/libros/{libro_id}", status_code=204)
def borrar_libro(libro_id: int):
    libro = buscar_libro(libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    libros.remove(libro)
    guardar()