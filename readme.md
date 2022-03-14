# Common
With SolarManager you can automatically charge your Volkswagen ID car (e.g. ID.4) with solar electricity, even if your wallbox does not support this (like ID. Charger does not currently). There's an adapter for SolarEdge included but may be extended with another solar system easily.

It calculates from the current solar power, load and battery charge level if your car can be charged or not. If so it starts the charging process and if the sun goes down or you use more power for other things, it stops automatically.

The SolarManager is written in Python and uses [WeConnect-python](https://github.com/tillsteinbach/WeConnect-python) for the connection to the vehicle (ID.3, ID.4 and so on) and [SolarEdge API](https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf) for getting information about current solar power.

# Installation
Currently there's no package you can install easily. In future it's planed to have it as a package which installs everything itself. For the moment you can do the following to install it on a Raspberry Pi in headless mode.

TODO: Add steps to install

In the future there will be a package you can install and update easily.

# Documentation
## Configuration
In the config.txt file you find different entries you can or have to change.

### Needed configuration
|Section|Entry|Description|
|---|---|---|
|SolarEdge|ApiUrl|Add the API-Key for getting data from your SolarEdge installation. You can get this in the Admin area in your [SolarEdge-Monitoring-Plattform](https://monitoring.solaredge.com/)||
|WeConnect|Username|Your username you use for login in the WeConnect ID App|
||Password|Your password you use for login in the WeConnect ID App|
|SolarManager|VIN|The vehicle identification number for the car you want to load with solar power. You find this in the WeConnect ID App in "My cars" view.|

### Optional configuration
|Section|Entry|Description|
|---|---|---|
|SolarManager|SolarCheckInterval|Interval for checking the state of the car and solar power.|
||MinBatteryLoadToStartCharging|Minimum battery load that charging will be started. Before this SolarManager won't start charging your car.|
||MinPowerToGridToStartCharging|Minium power to grid that charging will be started. Below this SolarManager will only start charging if battery load is 100%.|
||MaxPowerToGridToStopCharging|If your home uses more power SolarManager will stop charging your car. Value is negative because it's a power consumption.|
||MinBatteryLoad|Minium battery load you want to have. If battery loads goes below this, SolarManager will stop charging your car.|
||SimulationMode|You can enable simulation mode to only log everything without really start or stop charging your car.|
||VehicleNameSuffix|The suffix you need to add to your car's nickname (see below).|

## Enable/Disable SolarManager
As SolarManager can't know if you want to load your car with solar power only or just load it because you need a full battery, there's a switch you can use right from your WeConnect ID App. If you want SolarManager to be active for your car, please extend your car's nickname in the app with the suffix `(SMC)` (= SolarManager Control). If you want to disable SolarManager for your car, just remove the suffix again.

The reason for this nickname suffix is because it's the easiest way you can enable or disable SolarManager from everywhere without having access to your SolarManager instance running at your home.

## Plug your car
SolarManager needs a car in the Ready for Charging state. This means you have to plug your car to your wallbox and authorize the charging. Then stop it again to give control to SolarManager.

# Local Deployment
There's a docker container for running all the stuff in Python without need to install everything locally.
To start docker, open a new PowerShell as Administrator and change to `docker` directory. Then run `docker compose up -d`. To stop it, run `docker compose down`.

On first call it will build the image where the WeConnect-python will be installed. To force rebuild, just run `docker compose build --no-cache`.

After the container started, run `docker exec -it solarmanager-app-1 bash` to connect to container's terminal. There you can run the SolarManager code with `python ./main.py`.