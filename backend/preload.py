from fastapi import FastAPI, HTTPException, Header, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import Optional
import secrets
import requests
import csv
import os

carpeta = os.getcwd()
app = FastAPI()
pokeapi_url = "https://pokeapi.co/api/v2/pokemon?limit=1025"

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

#Conexión a DB: 
def hacer_preload():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM pokemon")
    total = cur.fetchone()[0]

    if total == 0:
        print("No hay info en la tabla 'pokemon', se hará preload...")
        response = requests.get(pokeapi_url).json()
        for idx, p in enumerate(response["results"]):
            poke_id = idx + 1
            name = p["name"].lower()
            cur.execute("INSERT INTO pokemon (pokeId, name) VALUES (?, ?)", (poke_id, name))
        con.commit()
        print("Base de datos poblada con nombres e IDs")
    else:
        print("Ya hay Pokémon en la base de datos. No preload")

    con.close()

