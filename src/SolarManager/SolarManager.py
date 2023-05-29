import logging
import json

from Helper import Helper
from SolarEdge import SolarEdge
from Sonnen import Sonnen
from SolarManager.Elements.enums import ChargingState

from weconnect import weconnect, addressable
from weconnect.elements.control_operation import ControlOperation
from weconnect.elements.enums import MaximumChargeCurrent
from weconnect.elements.charging_status import ChargingStatus
from weconnect.elements.plug_status import PlugStatus
from weconnect.elements.vehicle import Vehicle

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

        self.isCharging = False
        self.chargingChangeRequested = False

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

        self.logger.info("Initialize WeConnect")
        self.weConnect = weconnect.WeConnect(username=username, password=password, updateAfterLogin=False, loginOnInit=False)

        self.logger.info("Login to WeConnect")
        self.weConnect.login()
        self.weConnect.update()

        self.weConnect.addObserver(self.onWeConnectEvent, addressable.AddressableLeaf.ObserverEvent.VALUE_CHANGED
                          | addressable.AddressableLeaf.ObserverEvent.ENABLED
                          | addressable.AddressableLeaf.ObserverEvent.DISABLED)

    def __del__(self) -> None:
        self.logger.info("Del")
        self.weConnect.disconnect()

    def disconnect(self) -> None:
        self.logger.info("Disconnect")
        self.weConnect.disconnect()

    def onWeConnectEvent(self, element, flags):

        if isinstance(element, addressable.AddressableAttribute):
            if flags & addressable.AddressableLeaf.ObserverEvent.VALUE_CHANGED:
                if element.getGlobalAddress() == f"/vehicles/{self.vin}/domains/charging/chargingStatus/chargingState":
                    self.logger.info(f"Charging state changed to {element.value}.")

                    if not self.chargingChangeRequested:
                        self.logger.info("Charging state changed by user.")

                    self.chargingChangeRequested = False
                    self.isCharging = element.value == ChargingStatus.ChargingState.CHARGING
                    self.logger.info(f"Is charging: {self.isCharging}")

    def run(self) -> None:
        self.logger.info("Run")
        
        if self.dataSource == None:
            self.logger.warn("The data source is not initialized.")
            return

        currentVehicleState = self.updateVehicle()
        nickname = currentVehicleState.nickname.value

        if not nickname.lower().endswith(self.vehicleNameSuffix):
            self.logger.info(f"SolarManager not enabled for this car - nickname suffix '{self.vehicleNameSuffix}' missing (current nickname: {nickname}).")
            return

        if currentVehicleState.domains["charging"]["plugStatus"].plugConnectionState.value is not PlugStatus.PlugConnectionState.CONNECTED or currentVehicleState.domains["charging"]["plugStatus"].plugLockState.value is not PlugStatus.PlugLockState.LOCKED:
            self.logger.info("Vehicle is not connected to or not locked at the plug.")
            return

        currentSolarState = self.dataSource.get_current_state()
        self.logger.info(f"Current solar state: {json.dumps(currentSolarState)}")

        if self.isCharging:
            self.checkStopCharging(currentSolarState["loadToGridPower"], currentSolarState["batteryChargeLevel"], currentVehicleState)
        else:
            self.checkStartCharging(currentSolarState["loadToGridPower"], currentSolarState["batteryChargeLevel"], currentVehicleState)

    def updateVehicle(self) -> Vehicle:
        self.logger.info("Update vehicle")        
        self.weConnect.update()

        for vin, vehicle in self.weConnect.vehicles.items():
            if vin == self.vin:
                return vehicle

        return None

    def checkStartCharging(self, loadToGridPower: float, batteryChargeLevel: float, vehicle: Vehicle) -> None:
        self.logger.info("Check start charging")

        if loadToGridPower <= 0:
            self.logger.info(f"Load to grid is {loadToGridPower} -> do nothing")
            return

        if batteryChargeLevel < self.minBatteryLoadToStartCharging:
            self.logger.info(f"Battery charge level < {self.minBatteryLoadToStartCharging} (current: {batteryChargeLevel}) -> do nothing")
            return

        if vehicle.domains["charging"]["batteryStatus"].currentSOC_pct.value == 100:
            self.logger.info("Current vehicle SoC is 100 -> do nothing")
            return

        if vehicle.domains["charging"]["chargingStatus"].chargingState.value is not ChargingStatus.ChargingState.READY_FOR_CHARGING:
            self.logger.info("Vehicle is not ready for start charging.")
            return

        if loadToGridPower > self.minPowerToGridToStartCharging or batteryChargeLevel == 100:
            self.logger.info(f"Load to grid > {self.minPowerToGridToStartCharging} (current: {loadToGridPower}) or battery charge level is 100 -> start charging")
            self.charging(vehicle, ChargingState.On)
            return

    def checkStopCharging(self, loadToGridPower: float, batteryChargeLevel: float, vehicle: Vehicle) -> None:
        self.logger.info("Check stop charging")
        
        if batteryChargeLevel < self.minBatteryLoad:
            self.logger.info(f"Battery charge level < {self.minBatteryLoad} (current: {batteryChargeLevel}) -> stop charging")
            self.charging(vehicle, ChargingState.Off)
            return

        if loadToGridPower < self.maxPowerFromGridToStopCharging:
            self.logger.info(f"Load to grid < {self.maxPowerFromGridToStopCharging} (current: {loadToGridPower}) -> stop charging")
            self.charging(vehicle, ChargingState.Off)
            return

        if vehicle.domains["charging"]["batteryStatus"].currentSOC_pct.value == 100:
            self.logger.info("Current SoC is 100 -> stop charging")
            self.charging(vehicle, ChargingState.Off)
            return

        if vehicle.domains["charging"]["chargingStatus"].chargingState.value is not ChargingStatus.ChargingState.CHARGING:
            self.logger.info("Vehicle is not charging.")
            self.isCharging = False
            return

        self.logger.info("Charging still ok -> do nothing")

    def charging(self, vehicle: Vehicle, newState: ChargingState) -> None:
        self.logger.info(f"Charging: {newState}")

        self.logger.info("Setting vehicle charging target SoC to 100")
        if not self.simulationMode:
            vehicle.domains["charging"]["chargingSettings"].targetSOC_pct.value = 100

        self.logger.info(f"Setting vehicle max AC to {MaximumChargeCurrent.REDUCED}")
        if not self.simulationMode:
            vehicle.domains["charging"]["chargingSettings"].maxChargeCurrentAC.value = MaximumChargeCurrent.REDUCED

        if vehicle.controls.chargingControl is None or not vehicle.controls.chargingControl.enabled:
            self.logger.warn("Charging control is none or not enabled for vehicle!")
            return

        if newState == ChargingState.On:
            self.logger.info("Start charging")
            Helper.sendPushNotification("Info", "Start charging")

            if not self.simulationMode:
                vehicle.controls.chargingControl.value = ControlOperation.START

        else:
            self.logger.info("Stop charging")
            Helper.sendPushNotification("Info", "Stop charging")

            if not self.simulationMode:
                vehicle.controls.chargingControl.value = ControlOperation.STOP

        self.chargingChangeRequested = True
