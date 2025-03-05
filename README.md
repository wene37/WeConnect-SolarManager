# Common
With SolarManager you can automatically charge your Volkswagen ID car (e.g. ID.4) with solar electricity, even if your wallbox does not support this or is not that good in this. There are adapters for SolarEdge and Sonnen included but may be extended with another solar system easily.

It calculates from the current solar power, load and battery charge level if your car can be charged or not. If so it starts the charging process and if the sun goes down or you use more power for other things, it stops automatically. With the integrated web app you can see the logs of the current day and receive push notifications for different events.

The SolarManager is written in Python and uses [WeConnect-python](https://github.com/tillsteinbach/WeConnect-python) for the connection to the vehicle (ID.3, ID.4 and so on) and [SolarEdge API](https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf) or Sonnen API for getting information about current solar power.

# Installation
Do the following to install it for example on a Raspberry Pi in headless mode:

1. Connect to your Raspberry Pi with a terminal console as user 'pi' (change to user's home directory if needed).
2. Run `sudo apt update`.
3. Run `sudo apt full-upgrade`.
4. Run `sudo apt install python3-pip`.
5. Run `python -m venv WeConnect-SolarManager`.
6. Run `WeConnect-SolarManager/bin/pip install WeConnect-SolarManager`.
7. Set needed configuration entries in `./WeConnect-SolarManager/SolarManager/config.txt` (see [Needed configuration](#needed-configuration)).
8. Run `sudo python ./WeConnect-SolarManager/SolarManager/init.py` to install and start the service. A backup of your config file will be created automatically (see [Update](#update))
9. Open a browser and connect to your Raspberry Pi's IP on the configured port (e.g. https://192.168.0.3:5001) to check the logs at `./WeConnect-SolarManager/SolarManager/logs` if everything runs fine.

# Update
To install an updated version of WeConnect-SolarManager, just run `./WeConnect-SolarManager/bin/pip install WeConnect-SolarManager --upgrade` from user's home directory. After that you have to restart the service by running init command above again.
Please note that with an upgrade the `config.txt` will be overwritten. You can copy this to a file `config.txt.user`, which will be used then. But in this case you have to care about new and changed settings by yourself.

**HINT:** If you are upgrading from an older version not using python's virtual environments, please remove the old version manually and start installation from new.

# Documentation
## Configuration
In the config.txt file you find different entries you can or have to change.

### Needed configuration
|Section|Entry|Description|
|---|---|---|
|SolarManager|VIN|The vehicle identification number for the car you want to load with solar power. You find this in the WeConnect ID App in "My cars" view.|
||DataSource|The data source you want to read solar data from. Currently there are data sources for "SolarEdge" and "Sonnen" available.|
|SolarEdge|ApiKey|Add the API-Key for getting data from your SolarEdge installation. You can get this in the Admin area in your [SolarEdge-Monitoring-Plattform](https://monitoring.solaredge.com/)|
||LocationId|Add the Location-ID for getting data from your SolarEdge installation. You can get this in the Admin area in your [SolarEdge-Monitoring-Plattform](https://monitoring.solaredge.com/)|
|Sonnen|IP|The IP address where your Sonnen API is running.|
||Port|The port where your Sonnen API is running.|
|WeConnect|Username|Your username you use for login in the WeConnect ID App|
||Password|Your password you use for login in the WeConnect ID App|

### Optional configuration
|Section|Entry|Description|
|---|---|---|
|SolarManager|SolarCheckInterval|Interval for checking the state of the car and solar power.|
||MinBatteryLoadToStartCharging|Minimum battery load that charging will be started. Before this SolarManager won't start charging your car.|
||MinPowerToGridToStartCharging|Minium power to grid that charging will be started. Below this SolarManager will only start charging if battery load is 100%.|
||MaxPowerFromGridToStopCharging|If your home uses more power SolarManager will stop charging your car. Value is negative because it's a power consumption.|
||MinBatteryLoad|Minium battery load you want to have. If battery load goes below this, SolarManager will stop charging your car.|
||SimulationMode|You can enable simulation mode to only log everything without really start or stop charging your car.|
||VehicleNameSuffix|The suffix you need to add to your car's nickname (see below).|
|WebApp|Port|Port for the web app.|
||WebPushSubject|VAPID setting for push notifications.|
||WebPushPublicKey|VAPID setting for push notifications.|
||WebPushPrivateKey|VAPID setting for push notifications.|

## Enable/Disable SolarManager
As SolarManager can't know if you want to load your car with solar power only or just load it because you need a full battery, there's a switch you can use right from your WeConnect ID App. If you want SolarManager to be active for your car, please extend your car's nickname in the app with the suffix `(SMC)` (= SolarManager Control). If you want to disable SolarManager for your car, just remove the suffix again.

The reason for this nickname suffix is because it's the easiest way you can enable or disable SolarManager from everywhere without having access to your SolarManager instance running at your home.

## Plug your car
SolarManager needs a car in the Ready for Charging state. This means you have to plug your car to your wallbox and authorize the charging.

## Web App
In the web app you currently see the today's log entries and you can enable push notifications as well. Please note, that push notifications do not work in Edge/Chrome, as there is no valid SSL cert for the web app. Push notifications are tested on Firefox (Windows) and iOS (added to home screen from Safari).

# Tested with
- SolarEdge solar system with 12 kWh battery
- Volkswagen ID.4 1st MAX
- Volkswagen ID.Charger Connect
