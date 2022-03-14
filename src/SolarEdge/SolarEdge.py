import logging
import requests
import configparser
import json

class SolarEdge:
    def __init__(
        self,
        configFileName: str
    ) -> None:

        self.logger = logging.getLogger("SolarEdge")

        configParser = configparser.ConfigParser()
        configParser.read(configFileName)

        self.apiUrl = configParser.get("SolarEdge", "ApiUrl")

    def __del__(self) -> None:
        self.logger.info("Del")

    def get_current_state(self) -> None:
        self.logger.info("Get current state")
        
        response = requests.get(self.apiUrl)
        jsonString = response.text
        
        self.logger.debug(f"JSON: {jsonString}")

        apiData = json.loads(jsonString)["siteCurrentPowerFlow"]

        powerToGrid = 0

        for connection in apiData["connections"]:
            fromValue = connection["from"].lower()
            toValue = connection["to"].lower()

            if fromValue == "load" and toValue == "grid":
                powerToGrid = apiData["GRID"]["currentPower"]
                break
            if fromValue == "grid" and toValue == "load":
                powerToGrid = apiData["GRID"]["currentPower"] * -1
                break

        result = dict()
        result["loadToGridPower"] = powerToGrid
        result["batteryChargeLevel"] = apiData["STORAGE"]["chargeLevel"]

        return result
