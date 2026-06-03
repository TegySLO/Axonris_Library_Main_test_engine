import os
import time
from datetime import datetime

def cleanup_old_files(directory, max_age_hours=24):
    if not os.path.exists(directory):
        return

    current_time = time.time()
    deleted_count = 0
    freed_bytes = 0

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_age_hours = (current_time - os.path.getmtime(filepath)) / 3600
            
            if file_age_hours > max_age_hours:
                try:
                    size = os.path.getsize(filepath)
                    os.remove(filepath)
                    deleted_count += 1
                    freed_bytes += size
                except Exception as e:
                    print(f"[GARBAGE COLLECTOR] Napaka pri brisanju {filepath}: {e}")

    if deleted_count > 0:
        mb_freed = freed_bytes / (1024 * 1024)
        print(f"[GARBAGE COLLECTOR] V mapi '{os.path.basename(directory)}' je bilo izbrisanih {deleted_count} starih datotek. Sprostitev: {mb_freed:.2f} MB.")

if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Zagon Garbage Collectorja...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # 1. Čiščenje začasnih 3D renderjev in Rembg izrezov (starejše od 24 ur)
    temp_dir = os.path.join(base_dir, "Axonris_3D_Generator", "temp")
    cleanup_old_files(temp_dir, max_age_hours=24)
    
    # 2. Čiščenje starih, predelanih swarm ticketov (starejše od 24 ur)
    tickets_dir = os.path.join(base_dir, "Axonris_AI_Framework", "swarm_tickets")
    cleanup_old_files(tickets_dir, max_age_hours=24)
    
    print("[GARBAGE COLLECTOR] Čiščenje zaključeno.")
