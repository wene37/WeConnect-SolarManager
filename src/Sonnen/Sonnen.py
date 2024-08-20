import logging
import requests
import json

from Helper import Helper

class Sonnen:
    def __init__(
        self
    ) -> None:

        self.logger = logging.getLogger("Sonnen")

        configParser = Helper.loadConfig()

        apiUrl = configParser.get("Sonnen", "ApiUrl")
        ip = configParser.get("Sonnen", "IP")
        port = configParser.get("Sonnen", "Port")

        self.apiUrl = apiUrl.replace("{{IP}}", ip).replace("{{PORT}}", port)
        self.simulationMode = configParser.getboolean("SolarManager", "SimulationMode")

    def __del__(self) -> None:
        self.logger.info("Del")

    def get_current_state(self) -> None:
        self.logger.info("Get current state")
        
        if self.simulationMode:
            self.logger.info("Using simulation data")
            jsonString = Helper.readFile("Data/Sonnen.json")
        else:
            response = requests.get(self.apiUrl)
            jsonString = response.text
        
        self.logger.debug(f"JSON: {jsonString}")

        apiData = json.loads(jsonString)

        result = dict()
        result["loadToGridPower"] = apiData["GridFeedIn_W"] / 1000
        result["batteryChargeLevel"] = apiData["USOC"]

        return result
