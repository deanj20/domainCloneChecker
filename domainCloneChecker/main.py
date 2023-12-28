import sys
import time
from services.LoggingService import LoggingService
from services.ConfigService import ConfigService
from services.CloneDomainCheckerService import CloneDomainChecker
import os
import pyfiglet
from multiprocessing import Process, Manager
import logging

class Main:
    def __init__(self):
        # Initialize the Main class
        self.logger = LoggingService(__name__).getLogger()
        self.config = ConfigService().config

        # Add a couple of blank lines before printing the ASCII art
        self.logger.info("\n\n" + pyfiglet.figlet_format(self.config["appName"], width=200))

        # Set the output directory
        self.outputDir = "_output"

    def get_log_level(self):
        return getattr(logging, self.config.get("logLevel", "INFO").upper(), logging.INFO)

    def run(self):
        config_file = os.path.join("config", "config.json")
        self.checker = CloneDomainChecker(config_file, os.path.join(self.outputDir, "output.log"), self.logger)
        base_urls = self.checker.load_base_strings()
        
        if not base_urls:
            self.logger.error("No base strings found in config.json.")
            return

        self.logger.info("Number of base strings to check: " + str(len(base_urls)))
        self.logger.info("Number of char substitutions coded: " + str(self.checker.get_total_elements()))
        self.logger.info("Number of possibilities for char substitutions coded: " + str(self.checker.get_total_elements()))

        self.print_dynamic_output(self.checker, base_urls)
        self.checker.run()


    def print_dynamic_output(self, checker, base_urls):
        manager = Manager()
        shared_domains_found = manager.list()

        def check_domains(domains_to_check):
            for domain in domains_to_check:
                if checker.check_domain(domain):
                    shared_domains_found.append(domain)

    def print_domains(self, domains):
        self.logger.info("\nEnd of Run. Sites found:")
        colored_domains = [
            self.checker.colorize_output(domain) + "--found" for domain in domains
        ]
        colored_line = " ".join(colored_domains)
        self.logger.info(colored_line)





        total_urls = len(base_urls)

        processes = []
        for base_url in base_urls:
            domains_to_check = list(checker.generate_urls(base_url))
            process = Process(target=lambda: check_domains(domains_to_check))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        self.logger.info("Number of base strings to check: {}".format(total_urls))
        self.logger.info("Number of char substitutions coded: {}".format(len(checker.substitutions)))
        self.logger.info("Number of possibilities for char substitutions coded: {}".format(checker.get_total_elements()))

        self.print_domains(shared_domains_found)

# Create an instance of the Main class and run the program
myApp = Main()
myApp.run()
