# ZLATO PRAVILO #002: Protokol za Gradnjo Main Engina
# Datum: 2026-06-03
# Status: POTRJENO
# Kategorija: Protokoli, Procesi, Sistemske Zahteve

## Kaj JE Main Engine?
Main Engine je Vrhovni Kurator in Analitik (Središče Resnice).
NI 3D generator. NI chatbot. Je SISTEM za zbiranje, preverjanje in selekcijo 
programerskih praks, ki zagotavlja, da AI ne halucinira in ne išče bližnjic.

## Komponente Main Engina
1. **Swarm Manager** (swarm_manager.py) - Centralni nadzornik vseh botov
2. **QA Research Bot** (qa_research_bot.py) - Raziskovalec, ki gradi znanje
3. **Security Gatekeeper** (security_scanner.py) - Varnostni pregled vhodnih podatkov
4. **Garbage Collector** (garbage_collector.py) - Čistilec začasnih datotek
5. **GitHub Syncer** (github_syncer.py) - Sinhronizacija znanja v oblak
6. **Meta Dashboard** (meta_dashboard.py) - UI za nadzor sistema

## Pravila Delovanja
1. NIKOLI ne zaupaj podatkom brez preverjanja (Security Gatekeeper)
2. VEDNO preveri lokalno knjižnico PRED iskanjem na spletu (Context Awareness)
3. NIKOLI ne zaženi več kot 2 bota hkrati (Eco Mode - zaščita strojne opreme)
4. VSE ugotovitve se MORAJO zapisati v knjižnico kot "Zlata Pravila"
5. Ob izpadu sistema se ticketi avtomatsko obnovijo (Crash Recovery)

## Arhitektura Komunikacije
- Boti komunicirajo preko JSON datotek (swarm_tickets/)
- UI nikoli ne kliče AI direktno (decouplano z REST API)
- GitHub služi kot oblačni trezor za potrjeno znanje

## Zahteve za Inštalacijo
- Python 3.10+ z virtualnim okoljem
- Paketi: fastapi, uvicorn, openai, requests, beautifulsoup4, duckduckgo_search, psutil
- LM Studio z lokalnim LLM modelom (Qwen ali podobno)
- Git za sinhronizacijo z GitHub oblakom
