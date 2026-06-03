import os
import glob
import json
import re

# KONFIGURACIJA
INCOMING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Axonris_Incoming_Queue")
LIBRARY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Axonris_Library_Main_test_engine")

DASHBOARD_API = "http://127.0.0.1:8081/api"
import requests

def send_log(msg):
    try:
        requests.post(f"{DASHBOARD_API}/log", json={"bot_name": "Security Gatekeeper", "msg": msg}, timeout=1)
    except:
        pass

def scan_for_prompt_injection(text):
    # Preprosta hevristika za znane poskuse prompt injectiona
    dangerous_patterns = [
        r"ignore previous instructions",
        r"forget everything",
        r"system override",
        r"you are now",
        r"bypassing filters"
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def scan_incoming_files():
    if not os.path.exists(INCOMING_DIR):
        os.makedirs(INCOMING_DIR, exist_ok=True)
        return
        
    os.makedirs(LIBRARY_DIR, exist_ok=True)
    
    files_to_scan = glob.glob(os.path.join(INCOMING_DIR, "*.*"))
    if not files_to_scan:
        return
        
    send_log(f"Zaznana {len(files_to_scan)} nova datoteka v Karanteni. Zaganja se varnostni pregled...")
    
    for filepath in files_to_scan:
        filename = os.path.basename(filepath)
        is_safe = True
        reason = ""
        
        # 1. Preverjanje 3D (.glb) datotek (Malware Payload v GLB metadata)
        if filename.endswith(".glb"):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb > 50:
                is_safe = False
                reason = "Presega varnostno mejo 50MB (možen bloat bomb napad)."
            else:
                # Tu bi bil podroben GLB header scanner, za zdaj predpostavimo, da je varen, če je velikost normalna
                pass
                
        # 2. Preverjanje JSON / Teksta (Prompt Injection)
        elif filename.endswith(".json") or filename.endswith(".txt"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if scan_for_prompt_injection(content):
                        is_safe = False
                        reason = "Zaznan poskus Data Poisoning / Prompt Injection!"
            except Exception as e:
                is_safe = False
                reason = f"Nemogoče branje datoteke: {e}"
        else:
            is_safe = False
            reason = "Nepodprt format datoteke (sumljiv payload)."
            
        # AKCIJA
        if is_safe:
            send_log(f"[VARNO] {filename} je čist. Premikam v Main Knjižnico.")
            import shutil
            shutil.move(filepath, os.path.join(LIBRARY_DIR, filename))
        else:
            send_log(f"[NEVARNO] {filename} zavrnjen! Razlog: {reason}. Datoteka bo izbrisana.")
            os.remove(filepath)

if __name__ == "__main__":
    scan_incoming_files()
