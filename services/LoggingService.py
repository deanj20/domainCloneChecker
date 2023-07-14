from datetime import datetime, timezone
import logging
from logging.handlers import RotatingFileHandler
import os

class LoggingService:
    def __init__(self, name):
        self.logDirectory = os.path.join(os.getcwd(), "logs")

        if not os.path.exists(self.logDirectory):
            os.makedirs(self.logDirectory)

        date = datetime.now(timezone.utc)
        self.logPath = os.path.join(self.logDirectory, date.strftime("%Y%m%d") + "_" + name + ".log")

        #%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s
        #"%(asctime)s [%(levelname)s] %(message)s"
        self.log_formatter = logging.Formatter("%(asctime)s [%(levelname)s][%(funcName)s] %(message)s")

        self.my_file_handler = RotatingFileHandler(self.logPath, mode='a', maxBytes=5*1024*1024, 
                                        backupCount=2, encoding=None, delay=0)
        self.my_file_handler.setFormatter(self.log_formatter)
        self.my_file_handler.setLevel(logging.INFO)

        self.my_stream_handler = logging.StreamHandler()
        self.my_stream_handler.setFormatter(self.log_formatter)
        self.my_stream_handler.setLevel(logging.INFO)

        #getLogger is a singleton so it is possible to add duplicate handlers so we will check to make sure the handler does not exist before adding it.
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        hasStreamHandler = False
        hasFileHandler = False

        if len(self.logger.handlers) > 0:
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    hasStreamHandler = True
                if isinstance(handler, logging.FileHandler):
                    hasFileHandler = True

        if not hasStreamHandler:
            self.logger.addHandler(self.my_stream_handler)

        if not hasFileHandler:
            self.logger.addHandler(self.my_file_handler)

        # logging.basicConfig(
        #     level=logging.INFO,
        #     format="%(asctime)s [%(levelname)s] %(message)s",
        #     datefmt='%Y-%m-%d %H:%M:%S',
        #     handlers=[logging.FileHandler(self.logPath),
        #             logging.StreamHandler()])
        # self.logger = logging.getLogger(name)
        #This line isn't needed since we are no longer using scheduler: https://stackoverflow.com/questions/38102291/turn-off-logging-in-schedule-library
        #logging.getLogger('apscheduler').propagate = False

    
    def getLogger(self):
        return self.logger