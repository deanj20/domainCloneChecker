import json
import os
from services.LoggingService import LoggingService

class ConfigService:
    def __init__(self):
        self.logger = LoggingService(__name__).getLogger()
        self.configPath = os.path.join(os.getcwd(), 'config/config.json')
        #deserialize to python object.
        self.config = json.load(open(self.configPath))
        #self.logger.info(f"Init ConfigService: {__name__}")

    
    def saveConfig(self):
        self.saveConfigJsonObject(self.config)


    def saveConfigJsonString(self, jsonString):
        with open(self.configPath, "w") as jsonfile:
            jsonfile.write(jsonString)
            self.logger.info("Write successful")


    def saveConfigJsonObject(self, jsonObject):
        with open(self.configPath, "w") as jsonfile:
            json.dump(jsonObject, jsonfile)
            self.logger.info("Write successful")


    def getConfig(self):
        return self.config