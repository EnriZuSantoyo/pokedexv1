"""
FastAPI - Aplicación de ejemplo para practicar Backend

Esta pequeña aplicación tiene dos endpoints:
1. POST /login: Recibe usuario y contraseña, y retorna un token si son válidos.
2. GET /datos: Requiere autenticación por token en el header. Retorna datos dummy si el token es válido.

Para correr este ejemplo:
1. Instala Poetry si no lo tienes: https://python-poetry.org/docs/#installation
2. Crea el entorno: `poetry init` y luego instala FastAPI y Uvicorn:
   poetry add fastapi uvicorn
3. Ejecuta el servidor con:
   poetry run uvicorn main:app --reload

Luego puedes probar con curl o Postman los endpoints.
"""

from fastapi import FastAPI, HTTPException, Header, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from preload import hacer_preload
from pydantic import BaseModel
import sqlite3
from typing import Optional
import secrets
import requests
import csv
import os
import sys

carpeta = os.getcwd()
app = FastAPI()
pokeapi_url = "https://pokeapi.co/api/v2/pokemon?limit=1025"

HERE = os.path.dirname(__file__)
SRC_ROOT = os.path.dirname(HERE)
sys.path.append(SRC_ROOT)

from main import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pokedex.db")
con = sqlite3.connect(DB_PATH)


origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulación de base de datos de usuarios y tokens
# NUNCA JAMÁs se deben guardar datos sensibles en el código. Esto es solo un ejemplo.
# Con datos sensibles me refiero a contraseñas, usuarios, tokens de accesos a servicios.

USUARIOS_DB = {}
ruta_csv = "DB_USUARIOS.CSV"

USUARIOS_DB = {
    "usuario1": {"password": "1234", "token": "token123"},
    "usuario2": {"password": "abcd", "token": "token456"},
    "enrique": {"password": "1234", "token": "token789"},
}

# Datos dummy que queremos proteger con autenticación
DATOS_DUMMY = {
    "mensaje": "¡Bienvenido!",
    "notificaciones": 5,
    "rol": "estudiante",
}

RESPUESTA_ALTAS_OK = {
    "mensaje": "Usuario creado exitosamente"
}



    
# Modelo para el cuerpo del request del login
class Credenciales(BaseModel):
    usuario: str
    password: str


# Endpoint para iniciar sesión
@app.post("/login")
def login(credenciales: Credenciales):
    usuario = credenciales.usuario
    password = credenciales.password

    if usuario in USUARIOS_DB and USUARIOS_DB[usuario]["password"] == password:
        return {"token": USUARIOS_DB[usuario]["token"]}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")


# Función para verificar el token
def verificar_token(token: str) -> bool:
    for datos in USUARIOS_DB.values():
        if datos["token"] == token:
            return True
    return False


# Endpoint protegido
@app.get("/datos")
def obtener_datos(Authorization: Optional[str] = Header(None)):
    if not Authorization:
        raise HTTPException(
            status_code=401, detail="Token requerido en el header Authorization"
        )

    token = Authorization.replace(
        "Bearer ", ""
    )  # Por convención se usa 'Bearer <token>'
    if not verificar_token(token):
        raise HTTPException(status_code=403, detail="Token inválido")

    return DATOS_DUMMY

# Endpoint para agregar usuario
@app.post("/altas")
def agregar_usuario2(credenciales: Credenciales):
    username = credenciales.usuario
    passwd1 = credenciales.password
    #Verificamos si el usuario ya existe. Si no, lo agregamos. 
    if username in USUARIOS_DB:
        raise HTTPException(
            status_code=401, detail="El usuario ya existe"
        )
    else:
        with open(ruta_csv, "a", newline="", encoding="utf-8") as archivo:
            token = "token" + str(secrets.randbelow(1000))
            print(token)
            campos = [{'usuario': username,'password': passwd1, 'token': token}]
            nombresCampos = ['usuario', 'password', 'token']
            escritor = csv.DictWriter(archivo, fieldnames=nombresCampos)
            escritor.writerows(campos) # Agregamos el usuario al archivo .CSV
            USUARIOS_DB[username] = {"password": passwd1, "token": token} # Agregamos el usuario nuevo a la lista 
            print("\n✅ Usuario agregado correctamente")
            return RESPUESTA_ALTAS_OK


# Endpoint que llena inicialmente el dropdown de nombres e IDs de Pokémon que se usan
# en el dropdown
@app.get("/dropdown")
def llenar_dropdown():
    #Llamamos a preload.py para garantizar que haya info en la DB para llenar el dropdown 

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT pokeId,name from pokemon")
    lista = cur.fetchall()
    con.close()
    return [{"pokeId": row[0], "name": row[1]} for row in lista]



def formatear_fila(row):
    return {
        "pokeId": row[0],
        "type1": row[1],
        "type2": row[2],
        "name": row[3],
        "altura": row[4],
        "legendario": row[5],
        "peso": row[6],
        "sprite": row[7],
        "description": row[8],
        "generation": row[9]
    }



@app.get("/buscar")
def buscar_pokemon(busqueda):
    #Haremos un query a la DB con la información del Poke solicitado
    #Si existe, lo devolvemos todo en un JSON para desplegarlo
    #Si no existe, hacemos un llamado a la PokeAPI para traer sus datos
    #Y los guardamos en la DB 
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT pokeId,type1,type2,name,altura,legendario,peso,sprite,description,generation from pokemon WHERE name = '" + busqueda + "' ")
    lista = cur.fetchall()
    
    resultadoJson = [{"pokeId": row[0], "name": row[1], "type1": row[2], "type2": row[3], "altura": row[4], "legendario": row[5], "peso": row[6], "sprite": row[7], "description": row[8], "generation": row[9]} for row in lista]

    con.close()
    return resultadoJson


#Endpoint para llamar a PokeAPI por nombre y llenar la DB
@app.get("/pokemon/name/{nombre}")
def buscar_por_nombre(nombre: str):
    nombre = nombre.lower()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM pokemon WHERE name = ?", (nombre,))
    row = cur.fetchone()
    con.close()

    if not row or row[1] is None:
        buscarPokeapi(nombre)
        # Reintentar
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM pokemon WHERE name = ?", (nombre,))
        row = cur.fetchone()
        con.close()
        print(f"Retornando datos: {formatear_fila(row)}")
        if not row or row[1] is None:
            raise HTTPException(status_code=404, detail="No se pudo obtener el Pokémon")
        print(f"✅ Datos de {row[3]} encontrados y enviados")
    return formatear_fila(row)


#Endpoint para llamar a PokeApi por ID: 
@app.get("/pokemon/{pokeid}")
def buscar_por_id(pokeid: int):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM pokemon WHERE pokeId = ?", (pokeid,))
    row = cur.fetchone()
    con.close()

    if not row or row[1] is None:
        # Obtenemos el nombre para hacer búsqueda por nombre
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT name FROM pokemon WHERE pokeId = ?", (pokeid,))
        res = cur.fetchone()
        con.close()

        if not res:
            raise HTTPException(status_code=404, detail="No existe el Pokémon en la DB")
        nombre = res[0].lower()
        buscarPokeapi(nombre)

        # Intentamos traerlo
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM pokemon WHERE pokeId = ?", (pokeid,))
        row = cur.fetchone()
        con.close()
        print(f"Retornando datos: {formatear_fila(row)}")

        if not row or row[1] is None:
            raise HTTPException(status_code=404, detail="No se pudo obtener el Pokémon")
        print(f"Datos de {row[3]} encontrados y enviados")
    return formatear_fila(row)



# búsqueda PokeAPI
def buscarPokeapi(nombre):
    print(f"Buscando datos de {nombre} en la PokeAPI")

    try:
        datos = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nombre}").json()
        especie = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{nombre}").json()

        tipo1 = datos["types"][0]["type"]["name"] if len(datos["types"]) > 0 else None
        tipo2 = datos["types"][1]["type"]["name"] if len(datos["types"]) > 1 else None
        altura = datos["height"]
        peso = datos["weight"]
        sprite = datos["sprites"]["other"]["official-artwork"]["front_default"]

        descripcion = "Sin descripción"
        for entrada in especie["flavor_text_entries"]:
            if entrada["language"]["name"] == "es":
                descripcion = entrada["flavor_text"].replace("\n", " ").replace("\f", " ")
                break

        legendario = "Sí" if especie.get("is_legendary") else "No"
        generacion = especie["generation"]["name"]

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("""
            UPDATE pokemon SET
                type1 = ?, type2 = ?, altura = ?, legendario = ?, peso = ?,
                sprite = ?, description = ?, generation = ?
            WHERE LOWER(name) = ?
        """, (tipo1, tipo2, altura, legendario, peso, sprite, descripcion, generacion, nombre.lower()))
        con.commit()
        con.close()
        print(f"{nombre} actualizado correctamente en la DB")

    except Exception as e:
        print(f"Error al obtener datos de {nombre}: {e}")



# Leer el archivo CSV y convertirlo a una lista de diccionarios
def leer_usuarios(ruta_archivo: str = "DB_USUARIOS.CSV"):
    with open(ruta_archivo, newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        for linea in lector:
            nombre = linea["usuario"]
            USUARIOS_DB[nombre] = {
                "password": linea["password"],
                "token": linea["token"]
            }
        return list(USUARIOS_DB)  # ¿Por qué en el ejemplo casteábamos a List?


#USUARIOS_DB = leer_usuarios(ruta_csv)


