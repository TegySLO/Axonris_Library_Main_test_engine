import requests
import time
import json
import socket

DASHBOARD_API = "http://127.0.0.1:8081/api"

def send_log(msg):
    try:
        requests.post(f"{DASHBOARD_API}/log", json={"bot_name": "Qwen 2.5", "msg": msg})
        print(f"[LOG] {msg}")
    except requests.exceptions.ConnectionError:
        print(f"[WARN] Dashboard API nedosegljiv: {msg}")
    except Exception as e:
        print(f"[ERROR] Napaka pri pošiljanju loga: {e}")

def start_task(task_id, human_desc, tech_desc, eta):
    try:
        requests.post(f"{DASHBOARD_API}/task/start", json={
            "task_id": task_id,
            "bot_name": "Qwen 2.5",
            "human_desc": human_desc,
            "tech_desc": tech_desc,
            "eta_seconds": eta
        })
    except requests.exceptions.ConnectionError:
        print(f"[WARN] Dashboard API nedosegljiv pri zagonu naloge {task_id}")
    except Exception as e:
        print(f"[ERROR] Napaka pri zagonu naloge: {e}")

def end_task(task_id):
    try:
        requests.post(f"{DASHBOARD_API}/task/end", json={"task_id": task_id})
    except requests.exceptions.ConnectionError:
        print(f"[WARN] Dashboard API nedosegljiv pri zaključku naloge {task_id}")
    except Exception as e:
        print(f"[ERROR] Napaka pri zaključku naloge: {e}")

def report_error(err_id, msg, status):
    try:
        requests.post(f"{DASHBOARD_API}/error", json={
            "error_id": err_id,
            "msg": msg,
            "status": status
        })
    except requests.exceptions.ConnectionError:
        print(f"[WARN] Dashboard API nedosegljiv pri prijavi napake {err_id}")
    except Exception as e:
        print(f"[ERROR] Napaka pri prijavi napake: {e}")

def simulate_qwen_analysis():
    send_log("Inicializacija Qwen modela...")
    time.sleep(1)
    
    # 1. Zagon naloge
    start_task("qwen_review_1", "Lokalni AI pregleduje C++ datoteke", "POST http://127.0.0.1:1234/v1/chat/completions (temp=0.2)", 15)
    
    send_log("Povezovanje z LM Studiom na port 1234...")
    time.sleep(2)
    
    # Namerna napaka za prikaz v dashboardu
    send_log("Opa, napaka pri prenosu JSON paketa!")
    report_error("err_json_1", "Napaka pri razčlenjevanju JSON podatkov iz C++ programa.", "UNRESOLVED")
    
    time.sleep(3)
    send_log("Zagon 'Auto-Fix' logike...")
    report_error("err_json_1", "Napaka pri razčlenjevanju JSON podatkov iz C++ programa.", "AUTO-FIXING")
    
    time.sleep(4)
    send_log("Napaka uspešno popravljena v lokalnem pomnilniku.")
    report_error("err_json_1", "Napaka pri razčlenjevanju JSON podatkov iz C++ programa.", "RESOLVED")
    
    time.sleep(2)
    send_log("Analiza zaključena. Predajam nazaj glavnemu sistemu.")
    
    # 2. Zakljucek naloge
    end_task("qwen_review_1")

if __name__ == "__main__":
    simulate_qwen_analysis()
