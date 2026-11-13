# API de la Biblioteca

API REST hecha con FastAPI para gestionar libros.

## Instalación
pip install -r requirements.txt

## Cómo correrla
uvicorn main:app --reload

Después abrí http://127.0.0.1:8000/docs para probarla.

## Endpoints
GET /, GET /libros, POST /libros, GET/PUT/PATCH/DELETE /libros/{id}