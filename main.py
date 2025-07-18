from fastapi import FastAPI, HTTPException, Header, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import Optional
import secrets
import requests
import csv
import os

## Cargaremos inicialmente los datos iniciales de los Pokémon una sola vez para llenar el Dropdown y la DB.

carpeta = os.getcwd()
app = FastAPI()

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



app = FastAPI()
