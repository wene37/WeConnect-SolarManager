#!/usr/bin/python

import configparser
import pathlib
import string
import os
import stat
from datetime import datetime

def initService(configFilePath: string, currentDirectoryPath: string):
    print("Init service.")

    print("Create a copy of current config file.")
    os.system("cp -rf " + configFilePath + " " + configFilePath + "-" + datetime.today().strftime('%Y%m%d'))

    serviceFilePath = "/lib/systemd/system/SolarManager.service"

    if os.path.exists(serviceFilePath):
        print("Stopping current service.")
        os.system("sudo systemctl stop SolarManager.service")

        print("Disabling current service.")
        os.system("sudo systemctl disable SolarManager.service")

        print("Delete existing service file at '" + serviceFilePath + "'.")
        os.remove(serviceFilePath)

    serviceFileContent = "[Unit]\nDescription=SolarManager\nAfter=multi-user.target\nStartLimitIntervalSec=120s\nStartLimitBurst=50\n\n[Service]\nType=simple\nWorkingDirectory={{WORKING_DIRECTORY}}\nUser=pi\nExecStart=/usr/bin/python ./main.py\nRestart=on-failure\nRestartSec=120s\n\n[Install]\nWantedBy=multi-user.target"
    serviceFileContent = serviceFileContent.replace("{{WORKING_DIRECTORY}}", currentDirectoryPath)
    
    with open(serviceFilePath, 'w') as f:
        print("Writing new service file at '" + serviceFilePath + "'.")
        f.write(serviceFileContent)

    os.chmod(serviceFilePath, 644)

    mainFilePath = currentDirectoryPath + "/main.py"
    st = os.stat(mainFilePath)
    os.chmod(mainFilePath, st.st_mode | stat.S_IEXEC)

    print("Register and start service.")
    os.system("sudo systemctl daemon-reload")
    os.system("sudo systemctl enable SolarManager.service")
    os.system("sudo systemctl start SolarManager.service")

    print("Init done. Please check the log files for errors.")

try:

    here = pathlib.Path(__file__).parent.resolve()
    configFilePath = (here / "config.txt")
    userConfigFilePath = (here / "config.txt.user")
    userConfigFile = pathlib.Path(userConfigFilePath)

    if userConfigFile.is_file():
        configFilePath = userConfigFilePath

    print("Using config file '" + str(configFilePath) + "'.")

    configParser = configparser.ConfigParser()
    configParser.read(configFilePath)
    
    vin = configParser.get("SolarManager", "VIN")
    locationId = configParser.get("SolarEdge", "LocationId")
    apiKey = configParser.get("SolarEdge", "ApiKey")
    userName = configParser.get("WeConnect", "Username")
    password = configParser.get("WeConnect", "Password")

    if not vin or not locationId or not apiKey or not userName or not password:
        print("Please set all needed configurations in config file and run this script again.")
        exit
    else:
        initService(str(configFilePath), str(here))

except Exception as e:
    raise e
