"""
Axonris 3D Generator - Trellis Windows-to-WSL Proxy Server

Ta skripta posluša TCP zahteve (JSON) iz C++ GUI programa na Windowsih
in asinhrono zažene dejanski proces za Microsoft TRELLIS v WSL2 (Ubuntu).
Na ta način C++ ne potrebuje zavedanja o WSL2 arhitekturi.
"""

import sys
import os
import socket
import json
import time
import shutil
try:
    from gradio_client import Client, handle_file
except ImportError:
    print("[TRELLIS_PROXY] Opozorilo: gradio_client ni nameščen. Zaženi: pip install gradio_client")

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

def generate_via_cloud(image_path, win_out_path, ssat_steps, slat_scale):
    print(f"[TRELLIS_PROXY] Uporabljam Cloud API (Hugging Face) za: {image_path}")
    try:
        client = Client("trellis-community/TRELLIS")
        
        print("[TRELLIS_PROXY] Pošiljam sliko v oblak...")
        # Klic API-ja
        # Uporablja paramatre: image, ssat_steps, slat_scale
        # Za gradio_client navadno posredujemo handle_file()
        result = client.predict(
                image=handle_file(image_path),
                ssat_steps=ssat_steps,
                slat_scale=slat_scale,
                api_name="/image_to_3d"
        )
        
        # Result je pot do zgenerirane datoteke v gradio temp mapi
        # Ali pa tuple (video, glb_path) odvisno od specifikacije HF Space-a.
        # Naredimo preprost pregled in kopiranje:
        if isinstance(result, tuple) or isinstance(result, list):
            glb_file = result[1] if len(result) > 1 else result[0]
        else:
            glb_file = result
            
        print(f"[TRELLIS_PROXY] Prejeto iz oblaka: {glb_file}")
        
        if os.path.exists(glb_file):
            shutil.copy(glb_file, win_out_path)
            return True, ""
        else:
            return False, "Datoteka z oblaka ne obstaja na disku."
            
    except Exception as e:
        return False, str(e)

def handle_client(conn, addr):
    print(f"[TRELLIS_PROXY] Povezan GUI: {addr}")
    try:
        data = conn.recv(16384).decode('utf-8')
        if not data:
            return
            
        request = json.loads(data)
        if request.get("action") == "generate":
            image_path = request.get("image_path")
            ssat_steps = request.get("geometry_resolution", 25) 
            slat_scale = request.get("threshold", 0.5) 
            
            win_out_path = image_path + "_output.glb"
            start_time = time.time()
            
            # Trenutno ROCm lokalno ne dela, zato vsilimo Cloud!
            success, error_msg = generate_via_cloud(image_path, win_out_path, ssat_steps, slat_scale)
            
            duration = time.time() - start_time
            
            if success and os.path.exists(win_out_path):
                response = {
                    "status": "success",
                    "mesh_path": win_out_path,
                    "duration_seconds": duration,
                    "device": "Cloud API (Hugging Face)"
                }
            else:
                response = {
                    "status": "error",
                    "message": f"Trellis Cloud generacija ni uspela.\nLog:\n{error_msg}",
                    "mesh_path": "",
                    "duration_seconds": duration,
                    "device": "Cloud API (Hugging Face)"
                }
            
            conn.sendall(json.dumps(response).encode('utf-8'))
            
    except Exception as e:
        print(f"[TRELLIS_PROXY] Napaka: {e}")
        err_res = {"status": "error", "message": str(e)}
        conn.sendall(json.dumps(err_res).encode('utf-8'))
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(1)
    print(f"[TRELLIS_PROXY] Poslušam za C++ na {SERVER_HOST}:{SERVER_PORT}...")
    
    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)

if __name__ == "__main__":
    start_server()
