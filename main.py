from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

libros = []
contador_id = 1


class LibroEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=60)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True


class Libro(LibroEntrada):
    id: int


@app.get("/")
def raiz():
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros")
def listar_libros():
    return libros


@app.post("/libros", status_code=201, response_model=Libro)
def crear_libro(datos: LibroEntrada):
    global contador_id
    libro = {"id": contador_id, **datos.model_dump()}
    contador_id += 1
    libros.append(libro)
    return libro