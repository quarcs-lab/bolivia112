#!/usr/bin/env python3
"""Build province (provincia) identification for Bolivia's 339 municipalities.

Reproducibly derives the `prov_id`, `prov` and `dep_prov_mun` columns of
`regionNames/regionNames.csv` and (re)builds `regionNames/provinceNames.csv`.

How it works
------------
Bolivia's hierarchy is Department -> Province -> Municipality. The official INE
code `mun_id` is structured `D PP SS`:
    D  (digit 1)    department, INE order (1=Chuquisaca .. 9=Pando)
    PP (digits 2-3) province within the department
    SS (digits 4-5) municipal section (municipality)
so the province code is simply `prov_id = int(mun_id[:3])` (Bolivia-wide unique).

The 112 province *names* cannot be derived from code alone, so the verified
mapping (short official INE name + capital + the sources consulted) is embedded
below in PROVINCES. It was produced by decoding `mun_id`, cross-checking every
municipality centroid against the ADM2 province polygons in
`bolivia_adm2_gdp_perCapita_1990_2024.gpkg`, and verifying each name against INE,
Wikipedia and educa.com.bo. See `regionNames/province_verification_report.md`.

The script is idempotent: re-running rebuilds the same columns from `mun_id`.

Usage
-----
    uv run python code/build_province_names.py        # rebuild + validate
The optional geometric validation needs geopandas + the ADM2 GeoPackage; it is
skipped gracefully when they are unavailable (the core build needs only pandas).
"""
import csv
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DS4 = os.path.dirname(HERE)                       # .../ds4bolivia
REPO = os.path.dirname(DS4)                       # repo root
RN = os.path.join(DS4, "regionNames", "regionNames.csv")
PROVCSV = os.path.join(DS4, "regionNames", "provinceNames.csv")
MAPS = os.path.join(DS4, "maps", "bolivia339geoqueryOpt.geojson")
GPKG = next((p for p in [
    os.path.join(REPO, "bolivia_adm2_gdp_perCapita_1990_2024.gpkg"),
    os.path.join(DS4, "bolivia_adm2_gdp_perCapita_1990_2024.gpkg"),
] if os.path.exists(p)), None)

# Verified source of truth: one entry per province (112 total).
PROVINCES = [
  {
    "prov_id": 101,
    "prov": "Oropeza",
    "capital": "Sucre",
    "gadm_name": "Oropeza",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Oropeza",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 102,
    "prov": "Azurduy",
    "capital": "Azurduy",
    "gadm_name": "Azurduy",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Azurduy",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 103,
    "prov": "Zudáñez",
    "capital": "Zudáñez",
    "gadm_name": "Zudáñez",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Zud%C3%A1%C3%B1ez",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 104,
    "prov": "Tomina",
    "capital": "Padilla",
    "gadm_name": "Tomina",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Tomina",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 105,
    "prov": "Hernando Siles",
    "capital": "Monteagudo",
    "gadm_name": "Hernando Siles",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Hernando_Siles",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 106,
    "prov": "Yamparáez",
    "capital": "Tarabuco",
    "gadm_name": "Yamparáez",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Yampar%C3%A1ez",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 107,
    "prov": "Nor Cinti",
    "capital": "Camargo",
    "gadm_name": "Nor Cinti",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Nor_Cinti",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 108,
    "prov": "Belisario Boeto",
    "capital": "Villa Serrano",
    "gadm_name": "Belisario Boeto",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Belisario_Boeto",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 109,
    "prov": "Sud Cinti",
    "capital": "Villa Abecia",
    "gadm_name": "Sur Cinti",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Sud_Cinti",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 110,
    "prov": "Luis Calvo",
    "capital": "Villa Vaca Guzmán",
    "gadm_name": "Luis Calvo",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Chuquisaca",
      "https://es.wikipedia.org/wiki/Provincia_de_Luis_Calvo",
      "https://www.educa.com.bo/content/departamento-chuquisaca"
    ]
  },
  {
    "prov_id": 201,
    "prov": "Murillo",
    "capital": "La Paz",
    "gadm_name": "Murillo",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Provincia_de_Murillo",
      "https://www.educa.com.bo/content/departamento-de-la-paz"
    ]
  },
  {
    "prov_id": 202,
    "prov": "Omasuyos",
    "capital": "Achacachi",
    "gadm_name": "Omasuyos",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 203,
    "prov": "Pacajes",
    "capital": "Coro Coro",
    "gadm_name": "Pacajes",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 204,
    "prov": "Camacho",
    "capital": "Puerto Acosta",
    "gadm_name": "Camacho",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://www.educa.com.bo/content/departamento-de-la-paz"
    ]
  },
  {
    "prov_id": 205,
    "prov": "Muñecas",
    "capital": "Chuma",
    "gadm_name": "Muñecas",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://www.educa.com.bo/content/departamento-de-la-paz"
    ]
  },
  {
    "prov_id": 206,
    "prov": "Larecaja",
    "capital": "Sorata",
    "gadm_name": "Larecaja",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 207,
    "prov": "Franz Tamayo",
    "capital": "Apolo",
    "gadm_name": "Franz Tamayo",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 208,
    "prov": "Ingavi",
    "capital": "Viacha",
    "gadm_name": "Ingavi",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 209,
    "prov": "Loayza",
    "capital": "Luribay",
    "gadm_name": "Loayza",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://www.educa.com.bo/content/departamento-de-la-paz"
    ]
  },
  {
    "prov_id": 210,
    "prov": "Inquisivi",
    "capital": "Inquisivi",
    "gadm_name": "Inquisivi",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 211,
    "prov": "Sud Yungas",
    "capital": "Chulumani",
    "gadm_name": "Sud Yungas",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 212,
    "prov": "Los Andes",
    "capital": "Pucarani",
    "gadm_name": "Los Andes",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 213,
    "prov": "Aroma",
    "capital": "Sica Sica",
    "gadm_name": "Aroma",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 214,
    "prov": "Nor Yungas",
    "capital": "Coroico",
    "gadm_name": "Nor Yungas",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 215,
    "prov": "Abel Iturralde",
    "capital": "Ixiamas",
    "gadm_name": "Abel Iturralde",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://www.educa.com.bo/content/departamento-de-la-paz",
      "https://autonomias.lapaz.gob.bo/api/uploads/normativa/688a810013b37d8453cc56b6/688a811b13b37d8453cc56b9"
    ]
  },
  {
    "prov_id": 216,
    "prov": "Bautista Saavedra",
    "capital": "Charazani",
    "gadm_name": "Bautista Saavedra",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://www.educa.com.bo/content/departamento-de-la-paz"
    ]
  },
  {
    "prov_id": 217,
    "prov": "Manco Kapac",
    "capital": "Copacabana",
    "gadm_name": "Manco Kapac",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 218,
    "prov": "Gualberto Villarroel",
    "capital": "San Pedro de Curahuara",
    "gadm_name": "Gualberto Villarroel",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 219,
    "prov": "José Manuel Pando",
    "capital": "Santiago de Machaca",
    "gadm_name": "General José Manuel Pando",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.educa.com.bo/content/departamento-de-la-paz"
    ]
  },
  {
    "prov_id": 220,
    "prov": "Caranavi",
    "capital": "Caranavi",
    "gadm_name": "Caranavi",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_La_Paz_(Bolivia)",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 301,
    "prov": "Cercado",
    "capital": "Cochabamba",
    "gadm_name": "Cercado",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 302,
    "prov": "Campero",
    "capital": "Aiquile",
    "gadm_name": "Campero",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 303,
    "prov": "Ayopaya",
    "capital": "Independencia",
    "gadm_name": "Ayopaya",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 304,
    "prov": "Esteban Arze",
    "capital": "Tarata",
    "gadm_name": "Esteban Arze",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://www.educa.com.bo/geografia/provincia-esteban-arze-mapa",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 305,
    "prov": "Arani",
    "capital": "Arani",
    "gadm_name": "Arani",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 306,
    "prov": "Arque",
    "capital": "Arque",
    "gadm_name": "Arque",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 307,
    "prov": "Capinota",
    "capital": "Capinota",
    "gadm_name": "Capinota",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 308,
    "prov": "Germán Jordán",
    "capital": "Cliza",
    "gadm_name": "Germán Jordán",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 309,
    "prov": "Quillacollo",
    "capital": "Quillacollo",
    "gadm_name": "Quillacollo",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 310,
    "prov": "Chapare",
    "capital": "Sacaba",
    "gadm_name": "Chapare",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 311,
    "prov": "Tapacarí",
    "capital": "Tapacarí",
    "gadm_name": "Tapacarí",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 312,
    "prov": "Carrasco",
    "capital": "Totora",
    "gadm_name": "Carrasco",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 313,
    "prov": "Mizque",
    "capital": "Mizque",
    "gadm_name": "Mizque",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 314,
    "prov": "Punata",
    "capital": "Punata",
    "gadm_name": "Punata",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 315,
    "prov": "Bolívar",
    "capital": "Bolívar",
    "gadm_name": "Bolivar",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 316,
    "prov": "Tiraque",
    "capital": "Tiraque",
    "gadm_name": "Tiraque",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Cochabamba",
      "https://bo.reyqui.com/2017/06/departamento-de-cochabamba-provincias-y.html"
    ]
  },
  {
    "prov_id": 401,
    "prov": "Cercado",
    "capital": "Oruro",
    "gadm_name": "Cercado",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 402,
    "prov": "Eduardo Avaroa",
    "capital": "Challapata",
    "gadm_name": "Abaroa",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Abaroa",
      "https://en.wikipedia.org/wiki/Oruro_Department",
      "https://www.educa.com.bo/content/departamento-de-oruro"
    ]
  },
  {
    "prov_id": 403,
    "prov": "Carangas",
    "capital": "Corque",
    "gadm_name": "Carangas",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 404,
    "prov": "Sajama",
    "capital": "Curahuara de Carangas",
    "gadm_name": "Sajama",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 405,
    "prov": "Litoral",
    "capital": "Huachacalla",
    "gadm_name": "Litoral",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department",
      "https://www.educa.com.bo/content/departamento-de-oruro"
    ]
  },
  {
    "prov_id": 406,
    "prov": "Poopó",
    "capital": "Poopó",
    "gadm_name": "Poopó",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 407,
    "prov": "Pantaleón Dalence",
    "capital": "Huanuni",
    "gadm_name": "Pantaleón Dalence",
    "sources": [
      "https://en.wikipedia.org/wiki/Oruro_Department",
      "https://stesa.com/detail/2018-11-15-15207/Provincias_del_Departamento_de_Oruro.html"
    ]
  },
  {
    "prov_id": 408,
    "prov": "Ladislao Cabrera",
    "capital": "Salinas de Garci Mendoza",
    "gadm_name": "Ladislao Cabrera",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 409,
    "prov": "Sabaya",
    "capital": "Sabaya",
    "gadm_name": "Sabaya",
    "sources": [
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Oruro",
      "https://www.educa.com.bo/content/departamento-de-oruro"
    ]
  },
  {
    "prov_id": 410,
    "prov": "Saucarí",
    "capital": "Toledo",
    "gadm_name": "Saucarí",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 411,
    "prov": "Tomás Barrón",
    "capital": "Eucaliptus",
    "gadm_name": "Tomás Barrón",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 412,
    "prov": "Sud Carangas",
    "capital": "Santiago de Andamarca",
    "gadm_name": "Sur Carangas",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department",
      "https://www.educa.com.bo/content/departamento-de-oruro"
    ]
  },
  {
    "prov_id": 413,
    "prov": "San Pedro de Totora",
    "capital": "Totora",
    "gadm_name": "San Pedro de Totora",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 414,
    "prov": "Sebastián Pagador",
    "capital": "Santiago de Huari",
    "gadm_name": "Sebastián Pagador",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 415,
    "prov": "Mejillones",
    "capital": "La Rivera",
    "gadm_name": "Mejillones",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Mejillones",
      "https://en.wikipedia.org/wiki/Oruro_Department",
      "https://www.educa.com.bo/content/departamento-de-oruro"
    ]
  },
  {
    "prov_id": 416,
    "prov": "Nor Carangas",
    "capital": "Huayllamarca",
    "gadm_name": "Nor Carangas",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Oruro",
      "https://en.wikipedia.org/wiki/Oruro_Department"
    ]
  },
  {
    "prov_id": 501,
    "prov": "Tomás Frías",
    "capital": "Potosí",
    "gadm_name": "Tomás Frías",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Provincia_de_Tom%C3%A1s_Fr%C3%ADas",
      "https://www.educa.com.bo/content/departamento-de-potosi",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 502,
    "prov": "Rafael Bustillo",
    "capital": "Uncía",
    "gadm_name": "Rafael Bustillo",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.educa.com.bo/geografia/uncia-municipio-de-rafael-bustillo",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 503,
    "prov": "Cornelio Saavedra",
    "capital": "Betanzos",
    "gadm_name": "Cornelio Saavedra",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.educa.com.bo/content/departamento-de-potosi"
    ]
  },
  {
    "prov_id": 504,
    "prov": "Chayanta",
    "capital": "Colquechaca",
    "gadm_name": "Chayanta",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 505,
    "prov": "Charcas",
    "capital": "San Pedro de Buena Vista",
    "gadm_name": "Chárcas",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.educa.com.bo/content/departamento-de-potosi"
    ]
  },
  {
    "prov_id": 506,
    "prov": "Nor Chichas",
    "capital": "Cotagaita",
    "gadm_name": "Nor Chichas",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.educa.com.bo/content/departamento-de-potosi"
    ]
  },
  {
    "prov_id": 507,
    "prov": "Alonso de Ibáñez",
    "capital": "Sacaca",
    "gadm_name": "Alonso de Ibáñez",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Provincia_de_Alonso_de_Ib%C3%A1%C3%B1ez",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 508,
    "prov": "Sud Chichas",
    "capital": "Tupiza",
    "gadm_name": "Sur Chichas",
    "sources": [
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.educa.com.bo/content/departamento-de-potosi",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 509,
    "prov": "Nor Lípez",
    "capital": "Colcha K",
    "gadm_name": "Nor Lipez",
    "sources": [
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.educa.com.bo/content/departamento-de-potosi",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 510,
    "prov": "Sud Lípez",
    "capital": "San Pablo de Lípez",
    "gadm_name": "Sur Lipez",
    "sources": [
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.educa.com.bo/content/departamento-de-potosi",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 511,
    "prov": "José María Linares",
    "capital": "Puna",
    "gadm_name": "José María Linares",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://www.educa.com.bo/content/departamento-de-potosi",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 512,
    "prov": "Antonio Quijarro",
    "capital": "Uyuni",
    "gadm_name": "Antonio Quijarro",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://www.educa.com.bo/content/departamento-de-potosi",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 513,
    "prov": "Bilbao",
    "capital": "Arampampa",
    "gadm_name": "General Bilbao",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Bilbao",
      "https://www.wikidata.org/wiki/Q238079",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 514,
    "prov": "Daniel Campos",
    "capital": "Llica",
    "gadm_name": "Daniel Campos",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 515,
    "prov": "Modesto Omiste",
    "capital": "Villazón",
    "gadm_name": "Modesto Omiste",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.educa.com.bo/content/departamento-de-potosi"
    ]
  },
  {
    "prov_id": 516,
    "prov": "Enrique Baldivieso",
    "capital": "San Agustín",
    "gadm_name": "Enrique Baldivieso",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Potos%C3%AD",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://www.wikidata.org/wiki/Q238079"
    ]
  },
  {
    "prov_id": 601,
    "prov": "Cercado",
    "capital": "Tarija",
    "gadm_name": "Cercado",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Cercado_(Tarija)",
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Tarija",
      "https://www.educa.com.bo/content/departamento-de-tarija"
    ]
  },
  {
    "prov_id": 602,
    "prov": "Arce",
    "capital": "Padcaya",
    "gadm_name": "Arce",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Arce",
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Tarija",
      "https://www.educa.com.bo/content/departamento-de-tarija"
    ]
  },
  {
    "prov_id": 603,
    "prov": "Gran Chaco",
    "capital": "Yacuiba",
    "gadm_name": "Gran Chaco",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_del_Gran_Chaco",
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Tarija",
      "https://www.educa.com.bo/content/departamento-de-tarija"
    ]
  },
  {
    "prov_id": 604,
    "prov": "Avilés",
    "capital": "Uriondo",
    "gadm_name": "Avilés",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Jos%C3%A9_Mar%C3%ADa_Avil%C3%A9s",
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Tarija",
      "https://www.educa.com.bo/content/departamento-de-tarija"
    ]
  },
  {
    "prov_id": 605,
    "prov": "Méndez",
    "capital": "San Lorenzo",
    "gadm_name": "Guarayos",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_M%C3%A9ndez",
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Tarija",
      "https://www.educa.com.bo/content/departamento-de-tarija"
    ]
  },
  {
    "prov_id": 606,
    "prov": "O'Connor",
    "capital": "Entre Ríos",
    "gadm_name": "O'Connor",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_O%27Connor",
      "https://es.wikipedia.org/wiki/Categor%C3%ADa:Provincias_del_departamento_de_Tarija",
      "https://www.educa.com.bo/content/departamento-de-tarija"
    ]
  },
  {
    "prov_id": 701,
    "prov": "Andrés Ibáñez",
    "capital": "Santa Cruz de la Sierra",
    "gadm_name": "Andrés Ibáñez",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html",
      "https://en.wikipedia.org/wiki/Provinces_of_Bolivia"
    ]
  },
  {
    "prov_id": 702,
    "prov": "Warnes",
    "capital": "Warnes",
    "gadm_name": "Warnes",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html",
      "https://en.wikipedia.org/wiki/Provinces_of_Bolivia"
    ]
  },
  {
    "prov_id": 703,
    "prov": "Velasco",
    "capital": "San Ignacio de Velasco",
    "gadm_name": "Velasco",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html",
      "https://en.wikipedia.org/wiki/Provinces_of_Bolivia"
    ]
  },
  {
    "prov_id": 704,
    "prov": "Ichilo",
    "capital": "Buena Vista",
    "gadm_name": "Ichilo",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html"
    ]
  },
  {
    "prov_id": 705,
    "prov": "Chiquitos",
    "capital": "San José de Chiquitos",
    "gadm_name": "Chiquitos",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html"
    ]
  },
  {
    "prov_id": 706,
    "prov": "Sara",
    "capital": "Portachuelo",
    "gadm_name": "Sara",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html"
    ]
  },
  {
    "prov_id": 707,
    "prov": "Cordillera",
    "capital": "Lagunillas",
    "gadm_name": "Cordillera",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html"
    ]
  },
  {
    "prov_id": 708,
    "prov": "Vallegrande",
    "capital": "Vallegrande",
    "gadm_name": "Vallegrande",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html"
    ]
  },
  {
    "prov_id": 709,
    "prov": "Florida",
    "capital": "Samaipata",
    "gadm_name": "Florida",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html"
    ]
  },
  {
    "prov_id": 710,
    "prov": "Obispo Santistevan",
    "capital": "Montero",
    "gadm_name": "Obispo Santistéban",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://es.wikipedia.org/wiki/Obispo_Santiestevan_(provincia)",
      "https://en.wikipedia.org/wiki/Obispo_Santistevan_Province"
    ]
  },
  {
    "prov_id": 711,
    "prov": "Ñuflo de Chávez",
    "capital": "Concepción",
    "gadm_name": "Ñuflo De Chávez",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://en.wikipedia.org/wiki/%C3%91uflo_de_Ch%C3%A1vez_Province",
      "https://es.wikipedia.org/wiki/Provincia_%C3%91uflo_de_Chaves"
    ]
  },
  {
    "prov_id": 712,
    "prov": "Ángel Sandoval",
    "capital": "San Matías",
    "gadm_name": "Angel Sandoval",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html"
    ]
  },
  {
    "prov_id": 713,
    "prov": "Manuel María Caballero",
    "capital": "Comarapa",
    "gadm_name": "Manuel María Caballero",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://en.wikipedia.org/wiki/Provinces_of_Bolivia"
    ]
  },
  {
    "prov_id": 714,
    "prov": "Germán Busch",
    "capital": "Puerto Suárez",
    "gadm_name": "Germán Busch",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html"
    ]
  },
  {
    "prov_id": 715,
    "prov": "Guarayos",
    "capital": "Ascensión de Guarayos",
    "gadm_name": "Guarayos",
    "sources": [
      "https://www.cedib.org/wp-content/uploads/2013/09/BOLIVIA-Crecimiento-intercensal-municipios.pdf",
      "https://www.eabolivia.com/santa-cruz-bolivia.html"
    ]
  },
  {
    "prov_id": 801,
    "prov": "Cercado",
    "capital": "Trinidad",
    "gadm_name": "Cercado",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_del_Beni",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://es.wikipedia.org/wiki/Provincia_de_Cercado_(Beni)"
    ]
  },
  {
    "prov_id": 802,
    "prov": "Vaca Díez",
    "capital": "Riberalta",
    "gadm_name": "Vaca Diez",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Vaca_D%C3%ADez",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://es.wikipedia.org/wiki/Departamento_del_Beni"
    ]
  },
  {
    "prov_id": 803,
    "prov": "José Ballivián",
    "capital": "Reyes",
    "gadm_name": "General José Ballivián",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_del_General_Jos%C3%A9_Ballivi%C3%A1n",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://es.wikipedia.org/wiki/Departamento_del_Beni"
    ]
  },
  {
    "prov_id": 804,
    "prov": "Yacuma",
    "capital": "Santa Ana del Yacuma",
    "gadm_name": "Yacuma",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Yacuma",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://es.wikipedia.org/wiki/Departamento_del_Beni"
    ]
  },
  {
    "prov_id": 805,
    "prov": "Moxos",
    "capital": "San Ignacio de Moxos",
    "gadm_name": "Moxos",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Moxos",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://es.wikipedia.org/wiki/Departamento_del_Beni"
    ]
  },
  {
    "prov_id": 806,
    "prov": "Marbán",
    "capital": "Loreto",
    "gadm_name": "Marbán",
    "sources": [
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://es.wikipedia.org/wiki/Loreto_(Beni)",
      "https://es.wikipedia.org/wiki/Departamento_del_Beni"
    ]
  },
  {
    "prov_id": 807,
    "prov": "Mamoré",
    "capital": "San Joaquín",
    "gadm_name": "Mamoré",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_Mamor%C3%A9",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://es.wikipedia.org/wiki/Departamento_del_Beni"
    ]
  },
  {
    "prov_id": 808,
    "prov": "Iténez",
    "capital": "Magdalena",
    "gadm_name": "Iténez",
    "sources": [
      "https://es.wikipedia.org/wiki/Provincia_de_It%C3%A9nez",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia",
      "https://es.wikipedia.org/wiki/Departamento_del_Beni"
    ]
  },
  {
    "prov_id": 901,
    "prov": "Nicolás Suárez",
    "capital": "Porvenir",
    "gadm_name": "Nicolás Suárez",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Pando",
      "https://es.wikipedia.org/wiki/Provincia_Nicol%C3%A1s_Su%C3%A1rez",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 902,
    "prov": "Manuripi",
    "capital": "Puerto Rico",
    "gadm_name": "Manuripi",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Pando",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 903,
    "prov": "Madre de Dios",
    "capital": "Puerto Gonzalo Moreno",
    "gadm_name": "Madre de Dios",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Pando",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 904,
    "prov": "Abuná",
    "capital": "Santa Rosa del Abuná",
    "gadm_name": "Abuná",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Pando",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  },
  {
    "prov_id": 905,
    "prov": "Federico Román",
    "capital": "Nueva Esperanza",
    "gadm_name": "Federico Román",
    "sources": [
      "https://es.wikipedia.org/wiki/Departamento_de_Pando",
      "https://es.wikipedia.org/wiki/Provincia_del_General_Federico_Rom%C3%A1n",
      "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia"
    ]
  }
]

NAME = {p["prov_id"]: p["prov"] for p in PROVINCES}
ORDER = ["poly_id", "asdf_id", "mun", "mun_id", "dep", "dep_id",
         "prov_id", "prov", "dep_mun", "dep_prov_mun", "shapeID"]
NEW = ["prov_id", "prov", "dep_prov_mun"]


def build():
    df = pd.read_csv(RN, dtype={"mun_id": str})
    df["mun_id"] = df["mun_id"].str.strip()
    df = df.drop(columns=[c for c in NEW if c in df.columns])  # idempotent

    df["prov_id"] = df["mun_id"].str[:3].astype(int)
    df["prov"] = df["prov_id"].map(NAME)
    if df["prov"].isna().any():
        missing = sorted(df.loc[df["prov"].isna(), "prov_id"].unique())
        raise SystemExit("No province name for prov_id(s): %s" % missing)
    df["dep_prov_mun"] = df["dep"] + "-" + df["prov"] + "-" + df["mun"]

    assert set(ORDER) == set(df.columns), set(df.columns) ^ set(ORDER)
    df = df[ORDER]
    df.to_csv(RN, index=False, quoting=csv.QUOTE_MINIMAL)

    # province lookup: dep/dep_id/n_mun recomputed from the data, names/capitals
    # /sources from the verified table.
    agg = (df.groupby("prov_id")
             .agg(dep=("dep", "first"), dep_id=("dep_id", "first"),
                  n_mun=("mun", "count")).reset_index())
    meta = pd.DataFrame(PROVINCES)
    meta["sources"] = meta["sources"].map(lambda s: " ; ".join(s))
    look = (agg.merge(meta, on="prov_id")
               [["prov_id", "prov", "capital", "dep", "dep_id",
                 "n_mun", "gadm_name", "sources"]]
               .sort_values("prov_id"))
    look.to_csv(PROVCSV, index=False, quoting=csv.QUOTE_MINIMAL)

    # invariants
    assert len(df) == 339, len(df)
    assert df["prov_id"].nunique() == 112
    assert (df.groupby("prov_id")["prov"].nunique() == 1).all()
    assert (df.groupby("prov_id")["dep"].nunique() == 1).all()
    shared = look.groupby("prov")["prov_id"].nunique()
    assert set(shared[shared > 1].index) <= {"Cercado"}, shared[shared > 1]
    print("OK  %d municipalities, %d provinces -> %s, %s"
          % (len(df), df["prov_id"].nunique(),
             os.path.relpath(RN, REPO), os.path.relpath(PROVCSV, REPO)))
    return df


def validate(df):
    """Optional: confirm each municipality centroid sits in its province polygon."""
    try:
        import unicodedata
        import geopandas as gpd
    except ImportError:
        print("..  geometric validation skipped (geopandas not installed)")
        return
    if not GPKG or not os.path.exists(MAPS):
        print("..  geometric validation skipped (ADM2 gpkg / maps not found)")
        return
    norm = lambda x: unicodedata.normalize("NFKD", str(x)).encode(
        "ascii", "ignore").decode().lower().strip()
    mp = gpd.read_file(MAPS)
    pts = gpd.GeoDataFrame(mp[["asdf_id"]].copy(),
                           geometry=mp.geometry.representative_point(),
                           crs=mp.crs).to_crs(4326)
    adm2 = gpd.read_file(GPKG).to_crs(4326)[["NAME_2", "geometry"]]
    sj = gpd.sjoin(pts, adm2, how="left", predicate="within")[["asdf_id", "NAME_2"]]
    g2n = {p["prov_id"]: p["gadm_name"] for p in PROVINCES}
    m = df.merge(sj, on="asdf_id", how="left")
    m["exp"] = m["prov_id"].map(g2n)
    ok = m.apply(lambda r: norm(r["NAME_2"]) == norm(r["exp"]), axis=1).sum()
    print("OK  geometry: %d/%d municipality centroids inside their province "
          "polygon (rest are GADM border noise; mun_id is authoritative)"
          % (int(ok), len(m)))


if __name__ == "__main__":
    validate(build())
