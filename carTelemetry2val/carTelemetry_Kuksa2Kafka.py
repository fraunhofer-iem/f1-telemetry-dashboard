from kafka import KafkaProducer
from json import dumps
from kuksa_client.grpc import VSSClient
import os, sys
import configparser
from datetime import datetime

scriptDir= os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(scriptDir, "../../"))

class Kuksa_Client():
    
    # Constructor
    def __init__(self, config):
        print("Init kuksa client...")
        
        if "kuksa_val" not in config:
            print("kuksa_val section missing from configuration, exiting")
            sys.exit(-1)

    def shutdown(self):
        self.client.stop()
        

def getKuksaDataByString(datapointString,datapointSave):
    try:
        #print(f"{datapointString} , {datapointSave}")
        return updates[datapointString].value
    except:
        return datapointSave


if __name__ == "__main__":
    producer=KafkaProducer(
        value_serializer=lambda m: dumps(m ).encode('utf-8'),
        acks=0,
        bootstrap_servers=['0.0.0.0:9092']
    )

    # def sendingDataToKafka(data):
    #     TOPIC_NAME = 'tester1234'
    #     for datapoint in data:
    #         producer.send(TOPIC_NAME, value={f"{datapoint[1]}":f"{datapoint[0]}"}) 
    
    def sendingDataToKafka(data):
        newTime=datetime.now()

        TOPIC_NAME = 'tester1234'
        dataDictionary={}

        for datapoint in data:
            dataDictionary.update({f"{datapoint[1]}":f"{datapoint[0]}"})
        producer.send(TOPIC_NAME, value=dataDictionary) 

        

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

    kuksaClient=Kuksa_Client(config)
    print("waiting for Data from Kuksa")
    kuksaConfig = config['kuksa_val']

    #initializing some variables
    speedDataName='Vehicle.Speed'
    frontLeftWingName='Vehicle.FrontLeftWingDamage'
    frontRightWingName='Vehicle.FrontRightWingDamage'
    tireWear_fl_name='Vehicle.Tire.FrontLeftWear'
    tireWear_fr_name='Vehicle.Tire.FrontRightWear'
    tireWear_rl_name='Vehicle.Tire.RearLeftWear'
    tireWear_rr_name='Vehicle.Tire.RearRightWear'
    fuelLevel_name='Vehicle.FuelLevel'
    rpm_name='Vehicle.RPM'
    lastLapTime_name='Vehicle.LastLapTime'

    initVal=0

    speed=[initVal,speedDataName]
    frontLeftWingDamage=[initVal,frontLeftWingName]
    frontRightWingDamage=[initVal,frontRightWingName]
    tireWear_rr=[initVal,tireWear_rr_name]
    tireWear_fl=[initVal,tireWear_fl_name]
    tireWear_fr=[initVal,tireWear_fr_name]
    tireWear_rl=[initVal,tireWear_rl_name]
    fuelLevel=[initVal,fuelLevel_name]
    rpm=[initVal,rpm_name]
    lastLapTime=[initVal,lastLapTime_name]

    # reading data and sending it
    with VSSClient(kuksaConfig.get('host'),kuksaConfig.getint('port')) as client:
        for updates in client.subscribe_current_values([
            speedDataName,
            frontLeftWingName,
            frontRightWingName,
            tireWear_rr_name,
            tireWear_rl_name,
            tireWear_fr_name,
            tireWear_fl_name,
            fuelLevel_name,
            rpm_name,
            lastLapTime_name
        ]):
            try:
                speed[0]=getKuksaDataByString(speedDataName,speed[0])
                frontLeftWingDamage[0]=getKuksaDataByString(frontLeftWingName,frontLeftWingDamage[0])
                frontRightWingDamage[0]=getKuksaDataByString(frontRightWingName,frontRightWingDamage[0])
                tireWear_fl[0]=getKuksaDataByString(tireWear_fl_name,tireWear_fl[0])
                tireWear_fr[0]=getKuksaDataByString(tireWear_fr_name,tireWear_fr[0])
                tireWear_rl[0]=getKuksaDataByString(tireWear_rl_name,tireWear_rl[0])
                tireWear_rr[0]=getKuksaDataByString(tireWear_rr_name,tireWear_rr[0])
                fuelLevel[0]=getKuksaDataByString(fuelLevel[1],fuelLevel[0])
                rpm[0]=getKuksaDataByString(rpm[1],rpm[0])
                lastLapTime[0]=getKuksaDataByString(lastLapTime[1],lastLapTime[0])
                
                data=[
                    speed,
                    frontLeftWingDamage,
                    frontRightWingDamage,
                    tireWear_rr, 
                    tireWear_rl, 
                    tireWear_fr, 
                    tireWear_fl,
                    fuelLevel,
                    rpm,
                    lastLapTime,
                    ]
                sendingDataToKafka(data)
                
            except Exception as e:
                print(e.args)
   

    
