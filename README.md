# Install Guide
## System Requirements
This Project was created and run in a Linux-Ubuntu VM. \
`Ubuntu Version 22.04.3`.

You will also need a :

* PS5.
* Router to connect the PS5 to the PC.
* The Game: F1 2021.


## First Time Setup 
1. Set up your VM for example with VMWare.

2. Run the following commands in your terminal to install the following:

    ```
    >  git) $sudo apt install git
    >  docker) $sudo apt install docker.io -y
    >  docker-compose) $sudo apt install docker-compose -y
    >  append user) $sudo usermod -aG docker $USER
    >  python3) $sudo apt install python3-pip
    ```
    
    Python-Dependecies:
    
    ```
    >  python3-cffi) $sudo apt install python3-cffi
    >  Telemetry-F1-2021: 0.3.0) $pip install Telemetry-F1-2021
    >  kuksa-client) $pip install kuksa-client
    >  Paho-MQtt) $pip install paho-mqtt
    >  Proton) $pip install python-qpid-proton
    >  Kafka) $pip install kafka-python
    >  InfluxDB Client) $pip install influxdb_client
    ```

3. Go into your game settings in the PS5.

    ```
    >  Enable the telemetry feature.
    >  We make note of the UDP port number (20778)
    >  Update the laptop/pc IP adress for UDP communication.
    ```

4. Setting up Grafana and InfluxDB: 

    (!IMPORTANT!) grafana login credentials can be seen in docker compose file -> username: admin | password: admins

    * Move into the [influxDB](./InfluxDB/) folder and run the following command

        ```
        $docker-compose up -d
        ```

    * Open a browser of your choice and enter the influxdb and grafana web userinterfaces. \ 
        You will need the VM IP and the dedecated port. As an example for me it was http://192.168.178.129:8086 for influxDB and for grafana it was http://192.168.178.129:3000.
    
    * influxDB: Just follow the initial setup guide and use the following informations:
        ```
        organization : F1
        bucket : TelemetryData
        ```

    * Afterwards a Token should appear. Copy it now or generate a new one later, you will need it for grafana.

        > Please copy and paste the organization, bucket and token into the config file.

    * Grafana: Login with the credentials as seen before. Then go to dashboards and create a new dashboard. 
    Here you get the chance to import a [Formel1.json](./imports/Formel%201-1701426043812.json) file. Go ahead and import the file which can be found in the [imports](./imports/) folder. \
    When asked for a datasource you have to add influxdb as your datasource.    

    * Setting up the datasource in grafana. 
        ```
        > Change the query language to Flux.
        > in HTTP under url you enter your influxdb url : for me it was http://192.168.178.129:8086 
        > You dont need anything in Auth
        > in InfluxDB Details you provide the organization, token and default bucket. 

        If done correctly you should get a notification after pressing save & exit 
        ```

5. Filling the Config file. \
First open the [config file](./carTelemetry2val/config/carTelemetry_feeder.ini) in the [config folder](./carTelemetry2val/config/) and enter the following:
    * `kuksa_val` :
        * host : the host ip address of the VM where the Databroker is running on. For me it was 127.0.0.1 (localhost)
        * port : The port you wish to feed/subscribe from. For example 55555
    * `listenerIPAddr` :
        * host : Here we need the IP address we have also seen in the PS5 Settings
    * `PS5_UDPPort` : 
        * port : Here we need the port we have also seen in the PS5 Settings
    * `influxDB` : 
        * token : This token can be generated in the influxDB browser-user-interface
        * bucket : The bucket name you have generated earlier in influxDB
        * org : The organization name you have generated earlier in influxDB


## After The First Time Setup
If you have setup your system for the first time then you can follow the next steps.

### Running the main-program/-s
1. Set up Kuksa and the feeder python file from [here](https://github.com/eclipse-kuksa/kuksa-incubation/tree/main/fone2val).
    ```
    Please visit the link to the Git of Kuksa and follow the instructions:
    https://github.com/eclipse-kuksa/kuksa-incubation/tree/main/fone2val
    ```


2. Starting the Kafka docker container: \
    Move into the [Kafka folder](./Kafka/) and run the following command:
    ```   
    $docker-compose up -d
    ```

3. Starting the grafana/influxDB docker container:
    Move into the [InfluxDB folder](./InfluxDB/) and run the following command:
    ```
    $docker-compose up -d
    ```
    
4. Start [Kuksa2Kafka.py](./carTelemetry2val/carTelemetry_Kuksa2Kafka.py) in the [carTelemetry2val folder](./carTelemetry2val/) by running the following command:

    ```
    $python3 carTelemetry_Kuksa2Kafka.py
    ```

5. Start [Kafka2InfluxDb.py](./carTelemetry2val/carTelemetry_Kafka2InfluxDb.py) in the [carTelemetry2val folder](./carTelemetry2val/) by running the following command:

    ```
    $python3 carTelemetry_Kafka2InfluxDb.py
    ```


7. Open grafana in the browser
    * Now you can adjust the dashboard-refresh rate of grafana itself. For me the sweetspot was at 200ms
## Useful Troubleshooting Tips:
* If anything seems to be strugling to start. Whether in the starting process or in the running/developed process, check if all docker container are running properly. If not, restart them.
* If an error occurs when add influx db as datasource, it may be helpful to switch to url http://influxdb:[INFLUXDB_PORT]

## Known Limitations
* After examination there might be a problem in the way the tank percentage value is calculated. Open for a pull-request

## Useful Documents
You can find usefull documentation about the game F1 in the [references folder](./carTelemetry2val/references/)
