#!/usr/bin/python

import logging
import logging.handlers
import configparser

from time import sleep
from SolarManager import SolarManager
from pathlib import Path

def log_setup():
    
    formatter = logging.Formatter("%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s")
    logLevel = logging.INFO

    log_handler = logging.handlers.TimedRotatingFileHandler("logs/SolarManager.log", when="midnight", interval=1, backupCount=30)
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logLevel)

    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logLevel)

log_setup()
LOG = logging.getLogger("SolarManager.Service")
LOG.info("Starting service.")

try:

    configFileName = "config.txt"
    userConfigFileName = "config.txt.user"
    userConfigFile = Path(userConfigFileName)

    if userConfigFile.is_file():
        LOG.info("Using user config file.")
        configFileName = userConfigFileName
    
    configParser = configparser.ConfigParser()
    configParser.read(configFileName)
    
    sleepTimeSeconds = configParser.getint("SolarManager", "SolarCheckInterval")
    solarManager = SolarManager.SolarManager(configParser.get("WeConnect", "Username"), configParser.get("WeConnect", "Password"), configFileName)

    while True:
        
        solarManager.run()

        LOG.info(f"Sleeping for {sleepTimeSeconds} seconds")
        sleep(sleepTimeSeconds)

except Exception as e:
    LOG.error(f"An error occured while running the service: {e}", exc_info=True)
    raise e
