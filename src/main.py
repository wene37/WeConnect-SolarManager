#!/usr/bin/python

import datetime
import os
import logging
import logging.handlers

from Helper import Helper
from time import sleep
from SolarManager import SolarManager
from pathlib import Path

def log_setup():
    
    formatter = logging.Formatter("%(asctime)s :: %(process)d :: %(name)s :: %(levelname)s :: %(message)s")
    logLevel = logging.INFO

    logFilePath = os.path.join(os.path.dirname(__file__), "logs/SolarManager.log")
    log_handler = logging.handlers.TimedRotatingFileHandler(logFilePath, when="midnight", interval=1, backupCount=30)
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logLevel)

    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logLevel)

log_setup()
LOG = logging.getLogger("SolarManager.Service")
LOG.info("Starting service.")

try:

    datetimeNow = datetime.datetime.now()
    datetimeNowString = datetimeNow.strftime("%Y-%m-%d %H:%M:%S")

    configParser = Helper.loadConfig()
    sleepTimeSeconds = configParser.getint("SolarManager", "SolarCheckInterval")
    lastServiceStart = configParser.get("Dynamic", "LastServiceStart", fallback="")

    if (lastServiceStart == "" or configParser.getboolean("SolarManager", "SimulationMode") == True):
        lastServiceStart = "1970-01-01 00:00:00"

    configParser.set("Dynamic", "LastServiceStart", datetimeNowString)
    Helper.writeConfig(configParser)

    if ((datetime.datetime.now() - datetime.datetime.strptime(lastServiceStart, "%Y-%m-%d %H:%M:%S")).total_seconds() < sleepTimeSeconds):

        LOG.info(f"Service was started recently. Sleeping for {sleepTimeSeconds} seconds.")
        sleep(sleepTimeSeconds)

    Helper.sendPushNotification("Info", "Starting service")    

    solarManager = SolarManager.SolarManager(configParser.get("WeConnect", "Username"), configParser.get("WeConnect", "Password"))

    while True:
        
        solarManager.run()

        LOG.info(f"Sleeping for {sleepTimeSeconds} seconds.")
        sleep(sleepTimeSeconds)

except Exception as e:
    LOG.error(f"An error occured while running the service: {e}", exc_info=True)
    Helper.sendPushNotification("Error", "An error occured while running the service.")
    raise e
