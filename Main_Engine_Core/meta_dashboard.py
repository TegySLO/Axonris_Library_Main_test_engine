import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import socket
import os
import psutil
import time
import requests
import subprocess
import threading

app = FastAPI(title="Axonris Meta-Dashboard V3 - REST API")

# GLOBALNO STANJE SISTEMA
SYSTEM_LOGS = ["[SISTEM] Nadzorna plošča inicializirana. Čakam na bove..."]
# Format errorja: {"id": "err_1", "msg": "Opis", "status": "UNRESOLVED" | "AUTO-FIXING" | "RESOLVED", "time": "12:00:00"}
ERROR_LOGS = {}
# Format taska: ključ = task_id, vrednost = dict z boti, ETA in opisi
ACTIVE_TASKS = {}
COMPLETED_TASKS = []
SEEN_COMPLETED_IDS = set()

# Pydantic modeli za API vhode
class TaskStart(BaseModel):
    task_id: str
    bot_name: str
    human_desc: str
    tech_desc: str
    eta_seconds: int

class TaskEnd(BaseModel):
    task_id: str

class LogEntry(BaseModel):
    bot_name: str
    msg: str

class ErrorEntry(BaseModel):
    error_id: str
    msg: str
    status: str  # UNRESOLVED, AUTO-FIXING, RESOLVED

def check_lm_studio():
    try:
        res = requests.get("http://127.0.0.1:1234/v1/models", timeout=0.5)
        if res.status_code == 200:
            data = res.json()
            if data.get("data") and len(data["data"]) > 0:
                model_name = data["data"][0]["id"].split("/")[-1]
                return f"ONLINE ({model_name})"
            return "ONLINE (No model loaded)"
        return "ERROR"
    except Exception:
        return "OFFLINE"

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

# --- API KONČNE TOČKE ZA BOTE ---

@app.post("/api/task/start")
async def start_task(task: TaskStart):
    ACTIVE_TASKS[task.task_id] = {
        "bot_name": task.bot_name,
        "human_desc": task.human_desc,
        "tech_desc": task.tech_desc,
        "start_time": time.time(),
        "eta_seconds": task.eta_seconds
    }
    time_str = time.strftime("%H:%M:%S")
    SYSTEM_LOGS.append(f"[{time_str}] [{task.bot_name}] Zagon: {task.human_desc}")
    return {"status": "ok"}

@app.post("/api/task/end")
async def end_task(task: TaskEnd):
    if task.task_id in ACTIVE_TASKS:
        info = ACTIVE_TASKS[task.task_id]
        COMPLETED_TASKS.append({
            "id": task.task_id,
            "bot_name": info["bot_name"],
            "human_desc": info["human_desc"],
            "tech_desc": info["tech_desc"],
            "remaining": "ZAKLJUČENO"
        })
        if len(COMPLETED_TASKS) > 5:
            COMPLETED_TASKS.pop(0)
        del ACTIVE_TASKS[task.task_id]
        return {"status": "ok", "msg": "Task closed"}
    return {"status": "error", "msg": "Task not found"}

@app.post("/api/log")
async def add_log(log: LogEntry):
    time_str = time.strftime("%H:%M:%S")
    msg = f"[{time_str}] [{log.bot_name}] {log.msg}"
    SYSTEM_LOGS.append(msg)
    if len(SYSTEM_LOGS) > 100:
        SYSTEM_LOGS.pop(0)
    return {"status": "ok"}

@app.post("/api/error")
async def update_error(err: ErrorEntry):
    time_str = time.strftime("%H:%M:%S")
    ERROR_LOGS[err.error_id] = {
        "msg": err.msg,
        "status": err.status,
        "time": time_str
    }
    return {"status": "ok"}

@app.post("/api/qa_bot/run")
async def run_qa_bot():
    """Zazene raziskovalnega bota kot locen proces v ozadju."""
    def run_script():
        try:
            bot_path = os.path.join(os.path.dirname(__file__), "qa_research_bot.py")
            venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Local_3D_Generator", "venv310", "Scripts", "python.exe")
            subprocess.run([venv_python, bot_path], check=False)
        except Exception as e:
            print(f"Napaka pri zagonu QA bota: {e}")

    threading.Thread(target=run_script, daemon=True).start()
    return {"status": "ok", "msg": "QA Bot zagnan v ozadju"}

# --- API ZA FRONTEND V BRSKALNIKU ---

@app.get("/api/status")
async def get_status():
    import glob
    import json
    
    # 1. Preberi aktivne Swarm Tickete
    active_tasks_from_queue = []
    tickets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "swarm_tickets")
    if os.path.exists(tickets_dir):
        for f in glob.glob(os.path.join(tickets_dir, "*.json")):
            try:
                with open(f, "r", encoding="utf-8") as file:
                    ticket = json.load(file)
                    # Če je ticket v teku ali PENDING
                    if ticket.get("status") in ["IN_PROGRESS", "PENDING"]:
                        active_tasks_from_queue.append({
                            "bot_name": ticket.get("bot_role", "Unknown Bot"),
                            "human_desc": ticket.get("instruction", "Ni opisa")[0:50] + "...",
                            "tech_desc": ticket.get("task_type", "TASK"),
                            "remaining": "Izvajam..." if ticket.get("status") == "IN_PROGRESS" else "Čakam v vrsti"
                        })
                    elif ticket.get("status") == "COMPLETED":
                        tid = ticket.get("id", os.path.basename(f))
                        if tid not in SEEN_COMPLETED_IDS:
                            SEEN_COMPLETED_IDS.add(tid)
                            COMPLETED_TASKS.append({
                                "bot_name": ticket.get("bot_role", "Bot"),
                                "human_desc": ticket.get("instruction", "Ni opisa")[0:50] + "...",
                                "tech_desc": ticket.get("task_type", "TASK"),
                                "remaining": "ZAKLJUČENO"
                            })
            except Exception:
                pass
                
    # Omejimo COMPLETED_TASKS da UI ne bo prepoln
    while len(COMPLETED_TASKS) > 5:
        COMPLETED_TASKS.pop(0)

    # Združimo aktivne iz queue z našimi legacy ACTIVE_TASKS in COMPLETED_TASKS
    all_tasks = active_tasks_from_queue + COMPLETED_TASKS

    return {
        "lm_studio": check_lm_studio(),
        "trellis_server": "ONLINE" if check_port(5000) else "OFFLINE",
        "antigravity": "ACTIVE",
        "ram_usage": f"{psutil.virtual_memory().percent}%",
        "logs": SYSTEM_LOGS[-15:],
        "errors": list(ERROR_LOGS.values()),
        "active_tasks": all_tasks
    }

import os
dashboard_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard")
os.makedirs(dashboard_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")

if __name__ == "__main__":
    print("[META-DASHBOARD] Zaganjam napredni REST API nadzorni center na http://localhost:8081")
    uvicorn.run(app, host="0.0.0.0", port=8081)
