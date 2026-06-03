import os
import glob
import subprocess
import time
from datetime import datetime

# KONFIGURACIJA
LIBRARY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Axonris_Library_Main_test_engine")
TEMP_GENERATED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Axonris_3D_Generator", "temp")
GITHUB_REMOTE_URL = "https://github.com/TegySLO/Axonris_Library_Main_test_engine.git" # <--- Nastavi to

def init_git_repo(path):
    if not os.path.exists(os.path.join(path, ".git")):
        os.makedirs(path, exist_ok=True)
        subprocess.run(["git", "init"], cwd=path)
        print(f"[GITHUB SYNCER] Inicializiral nov prazen repozitorij v {path}")
        
        # Ustvari README, ce ga ni
        readme_path = os.path.join(path, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write("# Axonris 3D Library\n\nAvtomatsko zgenerirani modeli Main Engina.")
            subprocess.run(["git", "add", "README.md"], cwd=path)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=path)

def sync_to_github():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [GITHUB SYNCER] Preverjam nove datoteke za prenos v oblak...")
    
    os.makedirs(TEMP_GENERATED_DIR, exist_ok=True)
    os.makedirs(LIBRARY_DIR, exist_ok=True)
    
    init_git_repo(LIBRARY_DIR)
    
    # Najdi samo znanjske datoteke (md in json) v temp mapi
    new_files_found = False
    
    # Sestavimo listo vseh .md in .json datotek
    knowledge_files = glob.glob(os.path.join(TEMP_GENERATED_DIR, "*.md")) + glob.glob(os.path.join(TEMP_GENERATED_DIR, "*.json"))
    
    for filepath in knowledge_files:
        filename = os.path.basename(filepath)
        dest_path = os.path.join(LIBRARY_DIR, filename)
        
        # Premaknemo datoteko iz temp v naso git mapo
        try:
            import shutil
            shutil.copy2(filepath, dest_path)
            # BRISANJE ORIGINALA ZARADI PROSTORA NA LOKALNEM DISKU
            os.remove(filepath)
            new_files_found = True
            print(f"[GITHUB SYNCER] Dokument '{filename}' prevzet iz lokalnega sistema in dodan v Knjižnico Znanja.")
        except Exception as e:
            print(f"Napaka pri prenosu {filename}: {e}")
            
    if new_files_found:
        print("[GITHUB SYNCER] Pripravljam pošiljanje na GitHub oblak...")
        try:
            subprocess.run(["git", "add", "."], cwd=LIBRARY_DIR)
            commit_msg = f"Auto-Sync: Dodano novo potrjeno znanje ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=LIBRARY_DIR)
            
            # Če imamo remote url, ga pushamo
            if "POVEZAVA" not in GITHUB_REMOTE_URL:
                # Preveri, če je remote že dodan
                res = subprocess.run(["git", "remote", "-v"], cwd=LIBRARY_DIR, capture_output=True, text=True)
                if "origin" not in res.stdout:
                    subprocess.run(["git", "remote", "add", "origin", GITHUB_REMOTE_URL], cwd=LIBRARY_DIR)
                
                print("[GITHUB SYNCER] Pushing to GitHub (Cloud Knowledge Base)...")
                push_res = subprocess.run(["git", "push", "-u", "origin", "master"], cwd=LIBRARY_DIR)
                if push_res.returncode == 0:
                    print("[GITHUB SYNCER] USPEH! Znanje je varno v oblaku.")
                    # Tu bi lahko sprožili izbris tudi iz lokalnega LIBRARY_DIR, 
                    # a ga zaenkrat pustimo, da ga git lahko tracka, ali pa uporabimo git sparse-checkout.
            else:
                print("[GITHUB SYNCER] OPOZORILO: GitHub Remote URL ni nastavljen. Modeli so dodani v lokalni git trezor, a niso poslani v oblak.")
                
        except Exception as e:
            print(f"[GITHUB SYNCER] Napaka pri Git komandah: {e}")
    else:
        print("[GITHUB SYNCER] Ni novih modelov za sinhronizacijo.")

if __name__ == "__main__":
    sync_to_github()
