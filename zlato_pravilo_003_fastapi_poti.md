# ZLATO PRAVILO #003: FastAPI in Relativne Poti
# Datum: 2026-06-03
# Status: POTRJENO
# Kategorija: UI Strežniki, Python, Arhitektura

## Problem: Error 404 pri StaticFiles (Dashboard)
Pri izgradnji uporabniških vmesnikov z ogrodjem FastAPI in uporabi `StaticFiles` se pogosto pojavi napaka, kjer UI vrne "404 Not Found" za statične datoteke (npr. index.html), čeprav mapa obstaja. 

To se zgodi, ker AI modeli in programerji pogosto uporabijo **relativno pot**:
`app.mount("/", StaticFiles(directory="dashboard"))`

Če se skripta zažene iz druge mape (npr. iz `scripts/`), bo Python v trenutni delovni mapi (CWD) ustvaril novo prazno mapo `dashboard`, strežnik pa bo serviral to prazno mapo, namesto originalne mape projekta. To popolnoma poruši delovanje UI-ja.

## Rešitev: Absolutne Poti (Zlati Standard)
Da strežnik NIKOLI ne izgubi povezave do UI datotek (ne glede na to, od kod je skripta zagnana), je OBVEZNO uporabiti `os.path.dirname(__file__)` za kreiranje absolutne poti.

**Pravilna koda, ki jo moraš uporabiti:**
```python
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Preberi kje se nahaja trenutna skripta in pojdi eno mapo više (če je skripta v /scripts)
dashboard_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard")

# Montiraj absolutno pot
app.mount("/", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")
```

## Učinek za Sub Engina:
Ko te uporabnik vpraša, zakaj njegov FastAPI ne najde datotek ali vrača 404 prazno stran, mu nemudoma svetuj uporabo zgornjega kosa kode z absolutno potjo in `os.path.dirname`. Nikoli mu ne predlagaj rešitev z relativnimi stringi `"mapa/"`.
