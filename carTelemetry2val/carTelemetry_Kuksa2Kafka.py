import os
import sys
import json
import configparser
from datetime import datetime
from kafka import KafkaProducer
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import VSSClientError

# --- KONFIGURATION ---
KAFKA_BOOTSTRAP = ['kafka:9092'] # Für lokales Testing außerhalb von Docker auf ['localhost:29092'] ändern
KAFKA_TOPIC = 'tester1234'

DATAPOINTS = [
    'Vehicle.Speed',
    'Vehicle.FrontLeftWingDamage',
    'Vehicle.FrontRightWingDamage',
    'Vehicle.Tire.FrontLeftWear',
    'Vehicle.Tire.FrontRightWear',
    'Vehicle.Tire.RearLeftWear',
    'Vehicle.Tire.RearRightWear',
    'Vehicle.FuelLevel',
    'Vehicle.RPM',
    'Vehicle.LastLapTime'
]

# --- KAFKA CALLBACKS ---
def on_send_success(record_metadata):
    print(f"[KAFKA SUCCESS] Topic: {record_metadata.topic} | Partition: {record_metadata.partition} | Offset: {record_metadata.offset}")

def on_send_error(excp):
    print(f"[KAFKA ERROR] Failed to send message: {excp}", file=sys.stderr)

# --- KAFKA PRODUCER SETUP ---
def create_kafka_producer():
    print(f"[INIT] Connecting to Kafka at {KAFKA_BOOTSTRAP}...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda m: json.dumps(m).encode('utf-8'),
            acks=1,             # Leader-Bestätigung abwarten
            linger_ms=10,       # 10ms Buffering für effizientere Batches
            retries=3,          # Automatische Retries bei transienten Fehlern
            request_timeout_ms=5000
        )
        print("[INIT] Kafka Producer successfully created.")
        return producer
    except Exception as e:
        print(f"[FATAL] Could not create Kafka Producer: {e}", file=sys.stderr)
        sys.exit(-1)

# --- TESTING MODULE ---
def send_dummy_message(producer):
    print("\n--- INITIATING DUMMY TEST ---")
    dummy_payload = {
        "timestamp": datetime.now().isoformat(),
        "test_metric": 42.0,
        "status": "DUMMY_MESSAGE_SUCCESS"
    }
    print(f"[DUMMY] Sending payload: {dummy_payload}")
    
    # Blockierender Sendevorgang für den Test, um sofortiges Feedback zu erzwingen
    future = producer.send(KAFKA_TOPIC, value=dummy_payload)
    future.add_callback(on_send_success).add_errback(on_send_error)
    producer.flush()
    print("--- DUMMY TEST COMPLETED ---\n")

# --- CONFIG LOADER ---
def load_kuksa_config():
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    candidates = [
        '/config/carTelemetry_feeder.ini', 
        '/etc/carTelemetry_feeder.ini', 
        os.path.join(scriptDir, 'config/carTelemetry_feeder.ini'),
        os.path.join(scriptDir, '../../config/carTelemetry_feeder.ini') # Fallback für verschachtelte Struktur
    ]
    
    for candidate in candidates:
        if os.path.isfile(candidate):
            print(f"[INIT] Config found at: {candidate}")
            config = configparser.ConfigParser()
            config.read(candidate)
            if 'kuksa_val' not in config:
                print("[FATAL] 'kuksa_val' section missing in ini file.", file=sys.stderr)
                sys.exit(-1)
            return config['kuksa_val']
            
    print("[FATAL] No carTelemetry_feeder.ini configuration file found.", file=sys.stderr)
    sys.exit(-1)

# --- MAIN WORKER ---
def process_telemetry_stream(producer, kuksa_config):
    host = kuksa_config.get('host', '127.0.0.1')
    port = kuksa_config.getint('port', 55555)
    
    print(f"[INIT] Connecting to Kuksa Databroker at {host}:{port}...")
    
    # State-Dictionary zum Speichern der letzten bekannten Werte (verhindert Null-Werte bei asynchronen Updates)
    current_state = {dp: 0 for dp in DATAPOINTS}
    
    try:
        with VSSClient(host, port) as client:
            print("[KUKSA] Connected. Subscribing to datapoints...")
            
            # subscribe_current_values blockiert und yieldet bei neuen Daten
            for updates in client.subscribe_current_values(DATAPOINTS):
                
                # 1. State aktualisieren (Nur updaten, was im aktuellen Push enthalten ist)
                for dp in DATAPOINTS:
                    if dp in updates and updates[dp] is not None:
                        # Extrahiere reinen Wert aus Datapoint-Objekt
                        current_state[dp] = updates[dp].value
                
                # 2. Payload für Kafka vorbereiten
                # Hinzufügen eines Timestamps für InfluxDB/Zeitreihen-Analyse
                payload = {"timestamp": datetime.now().isoformat()}
                payload.update(current_state)
                
                print(f"[STREAM] Pushing to Kafka: {payload}")
                
                # 3. Asynchron an Kafka senden
                future = producer.send(KAFKA_TOPIC, value=payload)
                future.add_callback(on_send_success).add_errback(on_send_error)
                
    except VSSClientError as e:
        print(f"[KUKSA ERROR] Databroker Connection Lost/Failed: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[SYSTEM ERROR] Unexpected stream termination: {e}", file=sys.stderr)
    finally:
        print("[SHUTDOWN] Flushing remaining Kafka messages...")
        producer.flush()


if __name__ == "__main__":
    # 1. Init Kafka
    kafka_producer = create_kafka_producer()
    
    # 2. Debug/Verifizierung: Sende Dummy-Nachricht, um Kafka-Pipeline zu validieren
    send_dummy_message(kafka_producer)
    
    # 3. Init Kuksa Config
    kuksa_cfg = load_kuksa_config()
    
    # 4. Starte Data-Pipeline (Blockierend)
    process_telemetry_stream(kafka_producer, kuksa_cfg)