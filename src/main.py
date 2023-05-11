#!/usr/bin/python

import os
import logging
import logging.handlers

from Helper import Helper
from time import sleep
from SolarManager import SolarManager
from pathlib import Path

def log_setup():
    
    formatter = logging.Formatter("%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s")
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

    configParser = Helper.loadConfig()
    Helper.sendPushNotification("Info", "Starting service")

    sleepTimeSeconds = configParser.getint("SolarManager", "SolarCheckInterval")
    solarManager = SolarManager.SolarManager(configParser.get("WeConnect", "Username"), configParser.get("WeConnect", "Password"))

    while True:
        
        solarManager.run()

        LOG.info(f"Sleeping for {sleepTimeSeconds} seconds")
        sleep(sleepTimeSeconds)

except Exception as e:
    LOG.error(f"An error occured while running the service: {e}", exc_info=True)
    Helper.sendPushNotification("Error", "An error occured while running the service")
    raise e
