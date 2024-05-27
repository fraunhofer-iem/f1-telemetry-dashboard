import os, sys
import configparser

scriptDir= os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(scriptDir, "../../"))
from kafka import KafkaConsumer
from json import loads
import influxdb_client 
from influxdb_client.client.write_api import SYNCHRONOUS

TOPIC_NAME = 'tester1234'

consumer = KafkaConsumer(TOPIC_NAME, value_deserializer=lambda m: loads(m.decode('ascii')))
print("Initializing ...")


#config file checking
config_candidates=['/config/carTelemetry_feeder.ini', '/etc/carTelemetry_feeder.ini', os.path.join(scriptDir, 'config/carTelemetry_feeder.ini')]
for candidate in config_candidates:
    if os.path.isfile(candidate):
        configfile=candidate
        break
if configfile is None:
    print("No configuration file found. Exiting")
    sys.exit(-1)
config = configparser.ConfigParser()
config.read(configfile)
if "influxDB" not in config:
    print("influxDB section missing from configuration, exiting")
    sys.exit(-1)
influxConfig = config['influxDB']
listenerConfig = config['listenerIPAddr']

print("Initializing completed!")

#we can read json encoded data
msgKeys=['Vehicle.Speed',
         'Vehicle.FrontRightWingDamage',
         'Vehicle.FrontLeftWingDamage',
         'Vehicle.Tire.FrontLeftWear',
         'Vehicle.Tire.FrontRightWear',
         'Vehicle.Tire.RearLeftWear',
         'Vehicle.Tire.RearRightWear',
         'Vehicle.LastLapTime',
         'Vehicle.RPM',
         'Vehicle.FuelLevel',
         ]


bucket=influxConfig.get('bucket')
org =influxConfig.get('org')
token=influxConfig.get('token')
url="http://" + listenerConfig.get('host')+':8086'

client = influxdb_client.InfluxDBClient(url=url,token=token,org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

class DataSaveObject:
    def __init__(self, name):
        self.name=name
        self.value=0


saveArray=[]

def initSaves(keyList):
    for k in keyList:
        element= DataSaveObject(k)
        saveArray.append(element)
    return saveArray


def getAndSaveKafkaVal():
    for msg in consumer:
        msgData = msg.value
        speedPoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("speed",int(float(msgData['Vehicle.Speed'])))
        frontLeftWingDamagePoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("wingDamage_fl",int(float(msgData['Vehicle.FrontLeftWingDamage'])))
        frontRightWingDamagePoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("wingDamage_fr",int(float(msgData['Vehicle.FrontRightWingDamage'])))
        frontLeftTireWearPoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("wear_fl",int(float(msgData['Vehicle.Tire.FrontLeftWear'])))
        frontRightTireWearPoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("wear_fr",int(float(msgData['Vehicle.Tire.FrontRightWear'])))
        rearLeftTireWearPoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("wear_rl",int(float(msgData['Vehicle.Tire.RearLeftWear'])))
        rearRightTireWearPoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("wear_rr",int(float(msgData['Vehicle.Tire.RearRightWear'])))
        lastLapTimePoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("lastLapTime",int(msgData['Vehicle.LastLapTime']))
        fuelLevelPoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("fuel_lvl",int(float(msgData['Vehicle.FuelLevel'])))
        vehicleRPMPoint=influxdb_client.Point('Formula1_measurements').tag("metric","car").field("rpm",int(msgData['Vehicle.RPM']))
        
        datapoints=[speedPoint,
                    frontLeftWingDamagePoint,
                    frontRightWingDamagePoint,
                    frontLeftTireWearPoint,
                    frontRightTireWearPoint,
                    rearLeftTireWearPoint,
                    rearRightTireWearPoint, 
                    lastLapTimePoint,
                    fuelLevelPoint,
                    vehicleRPMPoint,
                    ]
        write_api.write(bucket=bucket,org=org,record=datapoints) 
        
               

if __name__ == '__main__':
    arr=initSaves(msgKeys)
    getAndSaveKafkaVal()

               
    

    
    
