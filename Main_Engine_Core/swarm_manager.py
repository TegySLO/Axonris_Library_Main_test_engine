import os
import json
import time
import requests
import uuid
import glob
from datetime import datetime
import subprocess

DASHBOARD_API = "http://127.0.0.1:8081/api"

def send_log(msg):
    try:
        requests.post(f"{DASHBOARD_API}/log", json={"bot_name": "Swarm Manager", "msg": msg}, timeout=1)
    except:
        pass

TICKETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "swarm_tickets")
os.makedirs(TICKETS_DIR, exist_ok=True)

def create_ticket(bot_role, task_type, instruction):
    ticket_id = f"TICKET_{uuid.uuid4().hex[:8]}"
    ticket = {
        "id": ticket_id,
        "bot_role": bot_role,
        "task_type": task_type,
        "instruction": instruction,
        "status": "PENDING",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "priority": 2,  # Default na medium (1=High, 2=Medium, 3=Low)
        "result": None
    }
    path = os.path.join(TICKETS_DIR, f"{ticket_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ticket, f, indent=4)
    msg = f"Ustvarjen nov ticket: {ticket_id} za {bot_role}"
    print(f"[SWARM MANAGER] {msg}")
    send_log(msg)
    return ticket_id

def check_system_health():
    # Preveri LM Studio
    lm_ok = False
    try:
        r = requests.get("http://127.0.0.1:1234/v1/models", timeout=2)
        if r.status_code == 200:
            lm_ok = True
    except:
        pass
        
    if not lm_ok:
        msg = "OPOZORILO: LM Studio ni odziven! Preverite strežnik."
        print(f"[AUTO-HEALER] {msg}")
        send_log(msg)
        
    return lm_ok

def assign_pending_tickets():
    # Omejitev: Nikoli ne zaženi več kot 2 bota hkrati (Eco Mode zaščita)
    import psutil
    active_bots = sum(1 for p in psutil.process_iter(['cmdline']) 
                      if p.info['cmdline'] and any('qa_research_bot' in str(c) for c in p.info['cmdline']))
    
    if active_bots >= 2:
        return  # Preveč aktivnih botov, čakamo
    
    pending_tickets = []
    
    for filepath in glob.glob(os.path.join(TICKETS_DIR, "*.json")):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                ticket = json.load(f)
                
            # AUTO-RECOVERY PROTOKOL:
            if ticket.get("status") == "IN_PROGRESS":
                updated_at_str = ticket.get("updated_at")
                if updated_at_str:
                    try:
                        updated_at = datetime.fromisoformat(updated_at_str)
                        if (datetime.now() - updated_at).total_seconds() > 1800: # 30 minut
                            ticket["status"] = "PENDING"
                            msg = f"CRASH RECOVERY: Ticket {ticket['id']} je bil predolgo v teku. Resetiran na PENDING."
                            print(f"[SWARM MANAGER] {msg}")
                            send_log(msg)
                            with open(filepath, "w", encoding="utf-8") as fw:
                                json.dump(ticket, fw, indent=4)
                    except:
                        pass
                
            if ticket.get("status") == "PENDING":
                pending_tickets.append((filepath, ticket))
                
        except Exception as e:
            pass
            
    # SORTIRANJE (Priority Queue)
    # Najprej sortiramo po 'priority' (1 je najvišja), nato po 'created_at' (najstarejši prvi)
    pending_tickets.sort(key=lambda x: (x[1].get("priority", 2), x[1].get("created_at", "")))
    
    # Procesiramo le toliko ticketov, kolikor imamo prostih "Eco Mode" slotov
    slots_available = 2 - active_bots
    
    for filepath, ticket in pending_tickets[:slots_available]:
        msg_assign = f"Zaznan PENDING ticket (Prioriteta {ticket.get('priority', 2)}): {ticket['id']}. Dodeljujem botu..."
        print(f"[SWARM MANAGER] {msg_assign}")
        send_log(msg_assign)
        
        ticket["status"] = "IN_PROGRESS"
        ticket["updated_at"] = datetime.now().isoformat()
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(ticket, f, indent=4)
        
        # Zaženi specializiranega bota
        if ticket.get("bot_role") == "QA_RESEARCHER":
            bot_path = os.path.join(os.path.dirname(__file__), "qa_research_bot.py")
            venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Local_3D_Generator", "venv310", "Scripts", "python.exe")
            
            subprocess.Popen([venv_python, bot_path, ticket["id"]])
            msg = f"QA Researcher zagnan za ticket {ticket['id']}."
            print(f"[SWARM MANAGER] {msg}")
            send_log(msg)

def main_loop():
    start_msg1 = "Main Engine Swarm nadzornik aktiviran."
    start_msg2 = "[ECO MODE] Pripravljen na auto-healing. Avtonomne raziskave so onemogočene (zaščita strojne opreme)."
    print(f"[SWARM MANAGER] {start_msg1}")
    print(f"[SWARM MANAGER] {start_msg2}")
    send_log(start_msg1)
    send_log(start_msg2)
    
    # Pridobimo pot do venv pythona in skript
    current_dir = os.path.dirname(__file__)
    gc_path = os.path.join(current_dir, "garbage_collector.py")
    security_path = os.path.join(current_dir, "security_scanner.py")
    venv_python = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "Local_3D_Generator", "venv310", "Scripts", "python.exe")
    
    last_gc_time = 0
    last_sec_time = 0

    while True:
        check_system_health()
        assign_pending_tickets()
        
        now = time.time()
        
        # Sproži Garbage Collector vsako uro (3600 sekund)
        if now - last_gc_time > 3600:
            if os.path.exists(gc_path):
                msg = "Zaganjam Garbage Collector..."
                print(f"[SWARM MANAGER] {msg}")
                send_log(msg)
                subprocess.Popen([venv_python, gc_path])
            last_gc_time = now
            
        # Sproži Security Gatekeeper vsakih 30 sekund
        if now - last_sec_time > 30:
            if os.path.exists(security_path):
                subprocess.Popen([venv_python, security_path])
            last_sec_time = now
            
        time.sleep(10) # Preverja vsakih 10 sekund

if __name__ == "__main__":
    main_loop()
