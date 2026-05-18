import logging
import json
import os

from Helper import Helper
from SolarEdge import SolarEdge
from Sonnen import Sonnen
from SolarManager.Elements.enums import ChargingState

from carconnectivity import carconnectivity
from carconnectivity.vehicle import ElectricVehicle
from carconnectivity.charging import Charging
from carconnectivity.charging_connector import ChargingConnector
from carconnectivity.observable import Observable
from carconnectivity.commands import GenericCommand
from carconnectivity.command_impl import ChargingStartStopCommand

# Disable image support in CarConnectivity and VW connector
# carconnectivity.SUPPORT_IMAGES = False
# carconnectivity.SUPPORT_ASCII_IMAGES = False
# try:
#     import carconnectivity_connectors.volkswagen.connector as vw_connector
#     vw_connector.SUPPORT_IMAGES = False
# except ImportError:
#     pass

class SolarManager:
    def __init__(
        self,
        username: str,
        password: str
    ) -> None:

        self.logger = logging.getLogger("SolarManager")

        configParser = Helper.loadConfig()

        self.minBatteryLoadToStartCharging = configParser.getfloat("SolarManager", "MinBatteryLoadToStartCharging")
        self.minPowerToGridToStartCharging = configParser.getfloat("SolarManager", "MinPowerToGridToStartCharging")
        self.maxPowerFromGridToStopCharging = configParser.getfloat("SolarManager", "MaxPowerFromGridToStopCharging")
        self.minBatteryLoad = configParser.getfloat("SolarManager", "MinBatteryLoad")
        self.simulationMode = configParser.getboolean("SolarManager", "SimulationMode")
        self.vin = configParser.get("SolarManager", "VIN")
        self.vehicleNameSuffix = configParser.get("SolarManager", "VehicleNameSuffix").lower()
        self.chargingChangeRequested = False
        self.ignoreDcCharging = configParser.getboolean("SolarManager", "IgnoreDcCharging")

        self.logger.info(f"Simulation mode: {self.simulationMode}")
        dataSource = configParser.get("SolarManager", "DataSource")

        if dataSource == "Sonnen":
            self.logger.info("Using 'Sonnen' as data source.")
            self.dataSource = Sonnen.Sonnen()
        elif dataSource == "SolarEdge":
            self.logger.info("Using 'SolarEdge' as data source.")
            self.dataSource = SolarEdge.SolarEdge()
        else:
            self.logger.error("The data source '{{DATA_SOURCE}}' does not exist. Set correct value in property 'DataSource' in the config file and restart the service.".replace("{{DATA_SOURCE}}", dataSource))
            self.dataSource = None
            return

        self.logger.info("Initialize CarConnectivity")
        tokenstore_file = os.path.join(os.path.dirname(__file__), "carconnectivity.token")
        config = {
            "carConnectivity": {
                "connectors": [
                    {
                        "type": "volkswagen",
                        "config": {
                            "username": username,
                            "password": password
                        }
                    }
                ]
            }
        }

        # Save root logger formatters before CarConnectivity overwrites them
        root_logger = logging.getLogger()
        saved_formatters = [(h, h.formatter) for h in root_logger.handlers]

        self.carConnectivity = carconnectivity.CarConnectivity(config=config, tokenstore_file=tokenstore_file)
        
        # Restore original formatters
        for handler, fmt in saved_formatters:
            handler.setFormatter(fmt)

        self.logger.info("Starting CarConnectivity")
        self.carConnectivity.startup()

        vehicle = self.updateVehicle()

        if vehicle is None:
            self.logger.warning("Vehicle not found.")
            return

        if not isinstance(vehicle, ElectricVehicle):
            self.logger.warning("Vehicle is not an electric vehicle.")
            return

        vehicle.charging.state.add_observer(
            self.onChargingStateChanged,
            flag=Observable.ObserverEvent.VALUE_CHANGED
        )

        self.isCharging = vehicle.charging.state.value == Charging.ChargingState.CHARGING
        self.logger.info(f"Vehicle charging when service started: {self.isCharging}")

    def __del__(self) -> None:
        self.logger.info("Del")
        self.carConnectivity.shutdown()

    def disconnect(self) -> None:
        self.logger.info("Disconnect")
        self.carConnectivity.shutdown()

    def onChargingStateChanged(self, element, flags):
        if flags & Observable.ObserverEvent.VALUE_CHANGED:
            self.logger.info(f"Charging state changed to {element.value}.")

            if not self.chargingChangeRequested:
                self.logger.info("Charging state changed by user.")

            self.chargingChangeRequested = False
            self.isCharging = element.value == Charging.ChargingState.CHARGING
            self.logger.info(f"Is charging: {self.isCharging}")

    def run(self) -> None:
        self.logger.info("Run")
        
        if self.dataSource is None:
            self.logger.warning("The data source is not initialized.")
            return

        currentVehicleState = self.updateVehicle()

        if currentVehicleState is None:
            self.logger.warning("Vehicle not found.")
            return

        if not isinstance(currentVehicleState, ElectricVehicle):
            self.logger.warning("Vehicle is not an electric vehicle.")
            return

        nickname = currentVehicleState.name.value or ""

        if not nickname.lower().endswith(self.vehicleNameSuffix):
            self.logger.info(f"SolarManager not enabled for this car - nickname suffix '{self.vehicleNameSuffix}' missing (current nickname: {nickname}).")
            return

        connector = currentVehicleState.charging.connector
        if connector.connection_state.value is not ChargingConnector.ChargingConnectorConnectionState.CONNECTED or connector.lock_state.value is not ChargingConnector.ChargingConnectorLockState.LOCKED:
            self.logger.info("Vehicle is not connected to or not locked at the plug.")
            return

        currentSolarState = self.dataSource.get_current_state()
        self.logger.info(f"Current solar state: {json.dumps(currentSolarState)}")

        if self.isCharging:
            self.checkStopCharging(currentSolarState["loadToGridPower"], currentSolarState["batteryChargeLevel"], currentVehicleState)
        else:
            self.checkStartCharging(currentSolarState["loadToGridPower"], currentSolarState["batteryChargeLevel"], currentVehicleState)

    def updateVehicle(self):
        self.logger.info("Update vehicle")

        try:
            self.carConnectivity.fetch_all()

            garage = self.carConnectivity.get_garage()
            if garage is not None:
                vehicle = garage.get_vehicle(self.vin)
                if vehicle is not None:
                    return vehicle

        except Exception as e:
            self.logger.error(f"Error updating vehicle: {e}")
        
        return None

    def getVehicleSoC(self, vehicle: ElectricVehicle):
        electric_drive = vehicle.get_electric_drive()
        if electric_drive is not None and electric_drive.level.enabled and electric_drive.level.value is not None:
            return electric_drive.level.value
        return None

    def checkStartCharging(self, loadToGridPower: float, batteryChargeLevel: float, vehicle: ElectricVehicle) -> None:
        self.logger.info("Check start charging")

        if loadToGridPower < -0.1:
            self.logger.info(f"Load to grid is {loadToGridPower} -> do nothing")
            return

        if batteryChargeLevel < self.minBatteryLoadToStartCharging:
            self.logger.info(f"Battery charge level < {self.minBatteryLoadToStartCharging} (current: {batteryChargeLevel}) -> do nothing")
            return

        vehicleSoc = self.getVehicleSoC(vehicle)
        if vehicleSoc is not None and vehicleSoc == 100:
            self.logger.info("Current vehicle SoC is 100 -> do nothing")
            return

        chargingState = vehicle.charging.state.value

        if chargingState not in [Charging.ChargingState.READY_FOR_CHARGING, Charging.ChargingState.CONSERVATION, Charging.ChargingState.OFF]:
            self.logger.info("Vehicle is not ready for start charging.")
            return

        if self.ignoreDcCharging and vehicle.charging.type.value == Charging.ChargingType.DC:
            self.logger.info("Vehicle is DC charging -> do nothing")
            return

        if loadToGridPower > self.minPowerToGridToStartCharging or batteryChargeLevel == 100:
            self.logger.info(f"Load to grid > {self.minPowerToGridToStartCharging} (current: {loadToGridPower}) or battery charge level is 100 -> start charging")
            Helper.sendPushNotification("Info", "Start charging")
            self.charging(vehicle, ChargingState.On)
            return

    def checkStopCharging(self, loadToGridPower: float, batteryChargeLevel: float, vehicle: ElectricVehicle) -> None:
        self.logger.info("Check stop charging")

        if self.ignoreDcCharging and vehicle.charging.type.value == Charging.ChargingType.DC:
            self.logger.info("Vehicle is DC charging -> do nothing")
            return
        
        if batteryChargeLevel < self.minBatteryLoad:
            self.logger.info(f"Battery charge level < {self.minBatteryLoad} (current: {batteryChargeLevel}) -> stop charging")
            Helper.sendPushNotification("Info", "Stop charging because of home battery charge level.")
            self.charging(vehicle, ChargingState.Off)
            return

        if loadToGridPower < self.maxPowerFromGridToStopCharging:
            self.logger.info(f"Load to grid < {self.maxPowerFromGridToStopCharging} (current: {loadToGridPower}) -> stop charging")
            Helper.sendPushNotification("Info", "Stop charging because power from grid.")
            self.charging(vehicle, ChargingState.Off)
            return

        vehicleSoc = self.getVehicleSoC(vehicle)
        if vehicleSoc is not None and vehicleSoc == 100:
            self.logger.info("Current SoC is 100 -> stop charging")
            Helper.sendPushNotification("Info", "Stop charging because SoC is 100.")
            self.charging(vehicle, ChargingState.Off)
            return

        if vehicle.charging.state.value is not Charging.ChargingState.CHARGING:
            self.logger.info("Vehicle is not charging.")
            self.isCharging = False
            return

        self.logger.info("Charging still ok -> do nothing")

    def charging(self, vehicle: ElectricVehicle, newState: ChargingState) -> None:
        self.logger.info(f"Charging: {newState}")

        self.logger.info("Setting vehicle charging target SoC to 100")
        if not self.simulationMode:
            vehicle.charging.settings.target_level.value = 100

        self.logger.info("Setting vehicle max charge current AC to reduced")
        if not self.simulationMode:
            vehicle.charging.settings.maximum_current.value = 6

        if vehicle.charging.commands is None or not vehicle.charging.commands.contains_command('start-stop'):
            self.logger.warning("Charging start-stop command is not available for vehicle!")
            return

        start_stop_command: GenericCommand = vehicle.charging.commands.commands['start-stop']
        if not isinstance(start_stop_command, ChargingStartStopCommand):
            self.logger.warning("Charging start-stop command is not of expected type!")
            return

        if newState == ChargingState.On:
            self.logger.info("Start charging")

            if not self.simulationMode:
                start_stop_command.value = ChargingStartStopCommand.Command.START

        else:
            self.logger.info("Stop charging")

            if not self.simulationMode:
                start_stop_command.value = ChargingStartStopCommand.Command.STOP

        self.chargingChangeRequested = True
