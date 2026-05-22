import os
import socket
import time
import pickle
import sys

TARGET_IP = os.getenv("TARGET_IP", "127.0.0.1")
TARGET_PORT = int(os.getenv("TARGET_PORT", 20777))
INPUT_FILE = os.getenv("INPUT_FILE", "/recorder/example-recordings/telemetry_dump.pkl")

try:
    with open(INPUT_FILE, "rb") as f:
        packets = pickle.load(f)
except FileNotFoundError:
    sys.exit(f"Dump-File {INPUT_FILE} nicht gefunden.")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"[*] Starte Endlos-Replay von {len(packets)} Paketen an {TARGET_IP}:{TARGET_PORT}...")

while True:
    start_time = time.perf_counter()
    
    for relative_timestamp, data in packets:
        target_time = start_time + relative_timestamp
        now = time.perf_counter()
        
        if target_time > now:
            time.sleep(target_time - now)
            
        sock.sendto(data, (TARGET_IP, TARGET_PORT))
        
    print("[*] Zyklus beendet. Starte neu...")
    # time.sleep(0.1) # Optional: Pufferzeit zwischen Zyklen zur Vermeidung von Network Spikes bei t=0