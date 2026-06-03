import requests
import time

DASHBOARD_API = "http://127.0.0.1:8081/api"

subagents = [
    {
        "task_id": "ag_sub_1",
        "bot_name": "Antigravity (Research)", 
        "human_desc": "TripoSR Quality Researcher", 
        "tech_desc": "Searching web for optimal TripoSR parameters and chunk_size...", 
        "eta_seconds": 600
    },
    {
        "task_id": "ag_sub_2",
        "bot_name": "Antigravity (SOTA)", 
        "human_desc": "Local AI Logic Analyzer", 
        "tech_desc": "Reviewing implementation_plan.md for TRELLIS.2 memory leaks", 
        "eta_seconds": 450
    },
    {
        "task_id": "ag_sub_3",
        "bot_name": "Antigravity (Logic)", 
        "human_desc": "C++ OpenGL Logic Analyzer", 
        "tech_desc": "Reviewing pending_shader.h for Base Color PBR mapping", 
        "eta_seconds": 500
    },
    {
        "task_id": "ag_sub_4",
        "bot_name": "Antigravity (ROCm)", 
        "human_desc": "AMD ROCm Trellis Installation Expert", 
        "tech_desc": "Finding spconv-rocm wheels for Ubuntu 22.04 WSL2", 
        "eta_seconds": 720
    }
]

def sync_subagents():
    print("[SYNC] Pošiljam Antigravity subagente v lokalni nadzorni center...")
    
    # 1. Objava v dnevnik
    requests.post(f"{DASHBOARD_API}/log", json={
        "bot_name": "Antigravity Main", 
        "msg": "Zaznanih 6 aktivnih subagentov. Sinhronizacija z UI..."
    })
    
    # 2. Registracija nalog
    for sa in subagents:
        try:
            requests.post(f"{DASHBOARD_API}/task/start", json=sa)
            print(f"Uspešno prijavljen: {sa['human_desc']}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Napaka pri prijavi {sa['task_id']}: {e}")

if __name__ == "__main__":
    sync_subagents()
