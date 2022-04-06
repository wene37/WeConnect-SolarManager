import logging
import requests
import configparser
import json

from datetime import datetime, timedelta

class GeoLocationManager:
    def __init__(
        self,
        configFileName: str
    ) -> None:

        self.logger = logging.getLogger("GeoLocationManager")

        configParser = configparser.ConfigParser()
        configParser.read(configFileName)

        self.geoLocationApiUrl = configParser.get("GeoLocation", "GeoLocationApi")
        self.sunsetApiUrl = configParser.get("GeoLocation", "SunsetApi")
        self.cacheHours = timedelta(hours=configParser.getint("GeoLocation", "CacheHours"))

        self.sunsetTime = None
        self.lastCheck = datetime.min

    def __del__(self) -> None:
        self.logger.info("Del")

    def GetSunsetTime(self) -> None:
        self.logger.info("GetSunsetTime")
        
        if self.sunsetTime is not None and self.lastCheck > datetime.now - self.cacheHours:

            self.logger.info(f"Returning cached sunset time '{self.sunsetTime}'.")
            return self.sunsetTime

        ipResponse = requests.get(self.geoLocationApiUrl)
        ipJsonString = ipResponse.text
        
        self.logger.debug(f"IP JSON: {ipJsonString}")

        location = str(json.loads(ipJsonString)["loc"]).split(",")

        sunsetReponse = requests.get(self.sunsetApiUrl + f"&lat={location[0]}&lng={location[1]}")
        sunsetJsonString = sunsetReponse.text

        self.logger.debug(f"Sunset JSON: {sunsetJsonString}")

        sunset = str(json.loads(sunsetJsonString)["results"]["sunset"])

        self.sunsetTime = datetime.strptime(sunset, '%Y-%m-%dT%H:%M:%S+00:00')
        self.lastCheck = datetime.now

        self.logger.info(f"Returning new sunset time '{self.sunsetTime}'.")

        return self.sunsetTime
