# Install Guide
## System Requirements
This is the Docker Solution of this Project.

You will also need a :

* PS5.
* Router to connect the PS5 to the PC.
* The Game: F1 2021.
* A docker ready environment


## First Time Setup 
### Please be sure to have a onetime internet connection at this point to download all dependencies.
1. Init submodule & run docker-compose
    ```
    git submodule update --init --recursive
    docker-compose up -d 
    ```

2. Go into your game settings in the PS5.

    ```
    >  Enable the telemetry feature.
    >  Enter the Port 20777
    ```

3. Setting up Grafana: 

    If your docker environment is running then you can:

    * Open your browser of choice and enter the grafana web userinterface. 
        ```
        localhost:3000
        ```
    
    * Grafana: Login with the credentials ```[admin : adminpassword]```. Then go to dashboards and find the F1 dashboard. 

4. Boot up the game and start playing to capture Data and watch the grafana UI change and accumulate with data

## Replay mode

You can find replay recording at /recorder/example-recordings/telemetry_dump.pkl. 

To start a replay recording in autoloop mode, you need to run the following command:

```
docker-compose --profile replay up -d
```


## Known Issues
* Please be sure to check if your firewall is allowing incoming UDP packets from 20777

## Useful Documents
You can find usefull documentation about the game F1 in the [references folder](./carTelemetry2val/references/)
