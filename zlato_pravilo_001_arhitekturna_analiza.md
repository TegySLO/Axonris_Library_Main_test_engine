# ZLATO PRAVILO #001: Kritična Analiza Main Engine Arhitekture
# Datum: 2026-06-03
# Status: POTRJENO (Pregledano z Claude Opus)
# Kategorija: Arhitekturna Analiza, Varnost, Optimizacija

## Ugotovitve

### KRITIČNA NAPAKA 1: meta_dashboard.py - Memory Leak
- **Problem:** Ob vsakem klicu `/api/status` (vsako sekundo) se COMPLETED ticketi ponovno dodajajo v globalno listo. To povzroča neskončno kumulacijo objektov.
- **Rešitev:** Preberi COMPLETED tickete le enkrat ali uporabi set() za preprečevanje duplikatov.

### KRITIČNA NAPAKA 2: security_scanner.py - Napačna pot knjižnice
- **Problem:** LIBRARY_DIR kaže na `Axonris_AI_Framework/Axonris_Library_Main_test_engine` namesto na `agentstudio/Axonris_Library_Main_test_engine`.
- **Rešitev:** Popravi relativno pot z dodanim `os.path.dirname()`.

### KRITIČNA NAPAKA 3: qa_research_bot.py - Neskončna zanka
- **Problem:** `while True` brez maksimalnega števila iteracij. Če Qwen halucinira tool_calls, bo bot v neskončni zanki.
- **Rešitev:** Dodaj `max_iterations = 10` varovalko.

### KRITIČNA NAPAKA 4: github_syncer.py - Napačen izvor datotek
- **Problem:** TEMP_GENERATED_DIR kaže na 3D Generator temp mapo. Main Engine ne producira znanja tam.
- **Rešitev:** Syncer mora brati iz pravilne mape ali pa se kliče ročno po tem, ko se znanje zapiše v knjižnico.

## Varnostna Tveganja
- API brez avtentikacije (meta_dashboard.py) - kdorkoli na omrežju lahko pošilja lažne podatke
- Plitka hevristika za Prompt Injection (security_scanner.py) - samo 5 besednih fraz
- subprocess.Popen brez omejitve vzporednih procesov (swarm_manager.py)

## Dobre Prakse (Kar deluje)
- JSON Ticket sistem za decouplanje UI od AI
- Crash Recovery z 30-minutnim timeoutom
- Eco Mode filozofija za omejen hardware
- Context Awareness (read_library pred search_web)
