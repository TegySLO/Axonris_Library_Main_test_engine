import os
import sys
import psutil
import datetime

LOG_FILE = "C:\\Users\\Blaz\\Desktop\\agentstudio\\Axonris_3D_Generator\\knowledge_base\\diagnostics.log"

def check_memory():
    mem = psutil.virtual_memory()
    return mem.percent

def log_event(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    print(log_entry.strip())

def run_diagnostics():
    log_event("Starting Engine V2 Diagnostics Check...")
    
    # Check RAM
    ram_usage = check_memory()
    log_event(f"System RAM Usage: {ram_usage}%")
    if ram_usage > 90:
        log_event("CRITICAL: System RAM is critically high! Potential VRAM spillover from local LLM.", "ERROR")
        
    # Check LM Studio local server (port 1234)
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        result = s.connect_ex(('127.0.0.1', 1234))
        if result == 0:
            log_event("LM Studio API is ONLINE on port 1234.")
        else:
            log_event("WARNING: LM Studio API is NOT responding on port 1234. Local Code Reviewer is unreachable.", "WARNING")

    # In the future: Add checks for WSL2 and Trellis Backend here
    log_event("Diagnostics Check Complete.")

if __name__ == "__main__":
    run_diagnostics()
