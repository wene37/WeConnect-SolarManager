#!/usr/bin/python

import configparser
import pathlib
import string
import os
import stat
from datetime import datetime

def initService(serviceName: string, serviceStartFile: string, virtualEnvPath: string):
    print("Init '" + serviceName + "' service.")

    serviceFilePath = "/lib/systemd/system/" + serviceName + ".service"

    if os.path.exists(serviceFilePath):
        print("Stopping existing service.")
        os.system("sudo systemctl stop " + serviceName + ".service")

        print("Disabling existing service.")
        os.system("sudo systemctl disable " + serviceName + ".service")

        print("Delete existing service file at '" + serviceFilePath + "'.")
        os.remove(serviceFilePath)

    serviceFileContent = "[Unit]\nDescription=" + serviceName + "\nAfter=multi-user.target\nStartLimitIntervalSec=120s\nStartLimitBurst=50\n\n[Service]\nType=simple\nWorkingDirectory=" + virtualEnvPath + "\nUser=pi\nExecStart=" + virtualEnvPath + "/bin/python ./SolarManager/" + serviceStartFile + "\nRestart=on-failure\nRestartSec=120s\n\n[Install]\nWantedBy=multi-user.target"
    
    with open(serviceFilePath, 'w') as f:
        print("Writing new service file at '" + serviceFilePath + "'.")
        f.write(serviceFileContent)

    os.chmod(serviceFilePath, 644)

    mainFilePath = virtualEnvPath + "/SolarManager/" + serviceStartFile
    st = os.stat(mainFilePath)
    os.chmod(mainFilePath, st.st_mode | stat.S_IEXEC)

    print("Register and start service.")
    os.system("sudo systemctl daemon-reload")
    os.system("sudo systemctl enable " + serviceName + ".service")
    os.system("sudo systemctl start " + serviceName + ".service")

    print("Init of '" + serviceName + "' done.")

def initSolarManagerService(configFilePath: string, virtualEnvPath: string):

    print("Create a copy of current config file.")
    os.system("cp -rf " + configFilePath + " " + configFilePath + "-" + datetime.today().strftime('%Y%m%d'))

    initService("SolarManager", "main.py", virtualEnvPath)

def initWebAppService(virtualEnvPath: string, port: int):

    initService("SolarManagerWebApp", "app.py", virtualEnvPath)
    print("Web app is running on this host on port " + str(port) + ".")

try:

    virtualEnvPath = pathlib.Path(__file__).parent.parent.resolve()
    configFilePath = (virtualEnvPath / "SolarManager/config.txt")
    userConfigFilePath = (virtualEnvPath / "SolarManager/config.txt.user")
    userConfigFile = pathlib.Path(userConfigFilePath)

    if userConfigFile.is_file():
        configFilePath = userConfigFilePath

    print("Using config file '" + str(configFilePath) + "'.")

    configParser = configparser.ConfigParser()
    configParser.read(configFilePath)
    
    vin = configParser.get("SolarManager", "VIN")
    userName = configParser.get("WeConnect", "Username")
    password = configParser.get("WeConnect", "Password")

    if not vin or not userName or not password:
        print("Please set all needed configurations in config file and run this script again.")
        exit
    else:
        initSolarManagerService(str(configFilePath), str(virtualEnvPath))
        initWebAppService(str(virtualEnvPath), configParser.getint("WebApp", "Port"))

except Exception as e:
    raise e
