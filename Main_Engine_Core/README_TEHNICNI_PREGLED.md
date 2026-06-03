# Axonris Main Engine - Arhitekturni Pregled (Whitepaper)

Dobrodošli v osrčju Axonris sistema. Ta repozitorij vsebuje surovo izvorno kodo **Main Engina**, centralnega "možganskega" vozlišča, ki smo ga zgradili za namene zbiranja, preverjanja in selekcije programerskih praks.
**POZOR:** To NI 3D generator (ki je strogo ločen projekt), temveč Multi-Agent Framework, ki nadzoruje umetno inteligenco in strojno opremo.

## 1. Arhitektura Sistema (JSON Ticket Swarm)
Jedro komunikacije temelji na datotečnem **JSON Ticket Sistemu** (mapa `swarm_tickets/`).
- Ni neposrednih (blocking) klicev med UI in LLM modelom.
- Nadzorna plošča (`meta_dashboard.py`) samo zapiše JSON datoteko.
- **Swarm Manager** (`swarm_manager.py`) opazuje mapo. Ko vidi nov ticket s statusom `PENDING`, zažene ustreznega agenta kot samostojen proces (Subprocess).
- S tem se UI nikoli ne zatakne (ne freeza), čeprav se v ozadju dogajajo masivne kompleksne operacije.

## 2. Eco Mode in Zaščita Strojne Opreme (RAM/CPU)
Zaradi uporabe masivnega lokalnega modela (Qwen 35B v LM Studiu), ki zasede ogromno VRAM/RAM spomina, je vgrajen strog nadzor porabe:
- Sistem **prepoveduje** paralelne in neskončne avtonomne raziskave (Loop prevention).
- Dokler bot aktivno ne potrebuje LLM-ja, procesi spijo.
- Vgrajen je `garbage_collector.py`, ki redno pregleduje začasne mape in preprečuje akumulacijo odmrlih procesov in začasnih datotek na disku.

## 3. Auto-Recovery Protokol (Odpornost na izpade)
Sistem je programiran z miselnostjo, da lahko osebni računalnik kadarkoli izgubi napajanje ali se sesuje.
- Swarm Manager pri vsakem ciklu pregleda tickete z oznako `IN_PROGRESS`.
- Če se posamezen ticket ni posodobil več kot 30 minut, to pomeni, da je bot pri obdelavi umrl (npr. zmanjkalo je RAM-a).
- Swarm Manager ga samodejno prevzame, mu vrne status `PENDING` in dodeli novemu botu. Nobena naloga se nikoli ne izgubi.

## 4. Varnost: Gatekeeper Karantena
Ker je ta GitHub repozitorij stičišče z uporabniki (ki imajo nameščene Sub-Engine inštalacije), obstaja tveganje za t.i. **Data Poisoning** ali **Prompt Injection** napade.
- Vgrajen je `security_scanner.py` (Varnostni Gatekeeper).
- Ta stoji med prejetimi datotekami (`incoming`) in glavno knjižnico (`Axonris_Library_Main`).
- Vsaka nova besedilna datoteka je strogo analizirana s hevristiko (zaznava skritih ukazov *"ignore previous instructions"*). Datoteke sumljivih velikosti so takoj uničene, preden bi obremenile Main Engine.

## 5. Zavedanje Konteksta (Context Awareness)
Boti v Main Enginu ne halucinirajo, preden uporabijo splet. 
Glavni raziskovalec (`qa_research_bot.py`) je opremljen z orodjem `read_library()`. Ima striktno navodilo v promptu, da **mora** najprej pregledati celotno lokalno zrcalno sliko GitHuba. Šele ko tam ne najde "zlatega pravila", gre raziskovat na internet s pomočjo DuckDuckGo (`search_web`).

---
*(Zgradil: Blaž v sodelovanju z AI Framework)*
