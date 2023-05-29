import logging
import requests
import json
import urllib.parse

from Helper import Helper

class SolarEdge:
    def __init__(
        self
    ) -> None:

        self.logger = logging.getLogger("SolarEdge")

        configParser = Helper.loadConfig()

        apiKey = configParser.get("SolarEdge", "ApiKey")
        locationId = configParser.get("SolarEdge", "LocationId")
        apiUrl = configParser.get("SolarEdge", "ApiUrl")

        self.apiUrl = apiUrl.replace("{{LOCATION_ID}}", urllib.parse.quote(locationId, safe='')).replace("{{API_KEY}}", urllib.parse.quote(apiKey, safe=''))
        self.simulationMode = configParser.getboolean("SolarManager", "SimulationMode")

    def __del__(self) -> None:
        self.logger.info("Del")

    def get_current_state(self) -> None:
        self.logger.info("Get current state")
        
        if self.simulationMode:
            self.logger.info("Using simulation data")
            jsonString = Helper.readFile("Data/SolarEdge.json")
        else:
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
