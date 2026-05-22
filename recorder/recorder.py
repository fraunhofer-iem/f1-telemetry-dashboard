import socket
import time
import pickle
import sys

# Konfiguration (muss mit PS5-Ausgabe übereinstimmen)
UDP_IP = "0.0.0.0"
UDP_PORT = 20777
OUTPUT_FILE = "example-recordings/telemetry_dump.pkl"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.settimeout(0.5)

try:
    sock.bind((UDP_IP, UDP_PORT))
except OSError as e:
    sys.exit(f"Port {UDP_PORT} belegt. Läuft der Feeder noch? Fehler: {e}")

packets = []
start_time = None

print(f"[*] Recorder lauscht auf {UDP_IP}:{UDP_PORT}...")
print("[*] Aufnahme läuft. Beenden und Speichern mit Ctrl+C.")

try:
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            print(f"[*] Paket received at {now:.2f}s. Size: {len(data):d} bytes")
            if start_time is None:
                start_time = now
                
            # Relative Zeit zum ersten Paket speichern
            packets.append((now - start_time, data))
        except:
            print("\n[*] Beende Aufnahme. Speichere Datenbasis...")
            with open(OUTPUT_FILE, "wb") as f:
                pickle.dump(packets, f)
            print(f"[*] {len(packets)} Pakete in {OUTPUT_FILE} gespeichert.")
        now = time.perf_counter()
        
        
        
        
except KeyboardInterrupt:
    print("\n[*] Beende Aufnahme. Speichere Datenbasis...")
    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump(packets, f)
    print(f"[*] {len(packets)} Pakete in {OUTPUT_FILE} gespeichert.")