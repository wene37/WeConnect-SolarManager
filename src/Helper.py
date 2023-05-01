import os
import configparser

from pathlib import Path

class Helper:

    @staticmethod
    def loadConfig() -> configparser:
        configFileName = "config.txt"
        userConfigFileName = "config.txt.user"
        userConfigFile = Path(os.path.join(os.path.dirname(__file__), userConfigFileName))

        if userConfigFile.is_file():
            #LOG.info("Using user config file '" + userConfigFileName + "'.")
            configFileName = userConfigFileName
        
        configFilePath = os.path.join(os.path.dirname(__file__), configFileName)
        configParser = configparser.ConfigParser()
        configParser.read(configFilePath)

        return configParser
