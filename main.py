# main.py

# Import necessary modules and classes
from services.LoggingService import LoggingService
from services.ConfigService import ConfigService
from services.CloneDomainCheckerService import CloneDomainChecker
import os
import pyfiglet


class Main:
    def __init__(self):
        # Initialize the Main class
        self.logger = LoggingService(__name__).getLogger()
        self.config = ConfigService().config
        self.logger.info(pyfiglet.figlet_format(self.config["appName"], width=200))

        # Set the input directory and file paths
        self.inputDir = os.path.join(os.getcwd(), "_input")
        self.outputDir = os.path.join(os.getcwd(), "_output")
        self.outputFile = os.path.join(self.outputDir, "imposterDomains.txt")
        
        self.logger.info(f"App init complete...")

    def run(self):
        # Execute the main program logic
        self.logger.info(f"App running...")

        # Define the base URLs to check
        base_urls = ["jdotek", "jdo-tek"]

        # Create the _output directory if it doesn't exist
        os.makedirs(self.outputDir, exist_ok=True)

        # Create an instance of CloneDomainChecker for each base URL and run it
        for base_url in base_urls:
            checker = CloneDomainChecker(tests=[base_url], outputFile=self.outputFile)
            checker.run()

        # Output the results


# Create an instance of the Main class and run the program
myApp = Main()
myApp.run()
