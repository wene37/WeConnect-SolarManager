import json
import os
import configparser

from pathlib import Path
from pywebpush import webpush, WebPushException
from datetime import datetime

class Helper:

    @staticmethod
    def getLogEntries():
        filePath = Path(os.path.join(os.path.dirname(__file__), "logs/SolarManager.log"))

        if filePath.is_file():
            with open(filePath) as file:
                return [line.rstrip() for line in file]

        return []

    @staticmethod
    def loadConfig() -> configparser:
        configFileName = "config.txt"
        userConfigFileName = "config.txt.user"
        userConfigFile = Path(os.path.join(os.path.dirname(__file__), userConfigFileName))

        if userConfigFile.is_file():
            configFileName = userConfigFileName
        
        configFilePath = os.path.join(os.path.dirname(__file__), configFileName)
        configParser = configparser.ConfigParser()
        configParser.read(configFilePath)

        return configParser

    @staticmethod
    def loadPushNotifications() -> json:
        fileName = "pushNotifications.json"
        filePath = Path(os.path.join(os.path.dirname(__file__), fileName))

        if filePath.is_file():
            with open(filePath) as json_file:
                return json.load(json_file)

        return json.loads('{"devices":[]}')

    @staticmethod
    def savePushNotifications(jsonObj: json) -> None:
        fileName = "pushNotifications.json"
        filePath = Path(os.path.join(os.path.dirname(__file__), fileName))

        with open(filePath, "w") as outfile:
            json.dump(jsonObj, outfile)

    @staticmethod
    def sendPushNotification(title: str, message: str) -> None:
        configParser = Helper.loadConfig()
        pushNotifications = Helper.loadPushNotifications()
        
        for device in pushNotifications["devices"]:

            subscription_information = {
                "endpoint": device["endpoint"],
                "keys": { "auth": device["auth"], "p256dh": device["p256dh"] }
            }

            data = json.dumps({"title": title, "message": message, "tag": "", "dateTime": datetime.utcnow()}, default=str)

            webpush(
                subscription_info=subscription_information,
                data=data,
                vapid_private_key=configParser.get("WebApp", "WebPushPrivateKey"),
                vapid_claims={"sub": configParser.get("WebApp", "WebPushSubject")}
            )
