import logging
import requests
import configparser
import json

class Sonnen:
    def __init__(
        self,
        configFileName: str
    ) -> None:

        self.logger = logging.getLogger("Sonnen")

        configParser = configparser.ConfigParser()
        configParser.read(configFileName)

        apiUrl = configParser.get("Sonnen", "ApiUrl")
        ip = configParser.get("Sonnen", "IP")
        port = configParser.get("Sonnen", "Port")

        self.apiUrl = apiUrl.replace("{{IP}}", ip).replace("{{PORT}}", port)

    def __del__(self) -> None:
        self.logger.info("Del")

    def get_current_state(self) -> None:
        self.logger.info("Get current state")
        
        response = requests.get(self.apiUrl)
        jsonString = response.text
        
        self.logger.debug(f"JSON: {jsonString}")

        apiData = json.loads(jsonString)

        result = dict()
        result["loadToGridPower"] = apiData["GridFeedIn_W"] / 1000
        result["batteryChargeLevel"] = apiData["USOC"]

        return result
