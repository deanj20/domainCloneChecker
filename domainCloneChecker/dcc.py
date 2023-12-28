#!/usr/bin/env python3

import sys
import time
import json
from services.LoggingService import LoggingService
from services.ConfigService import ConfigService
from services.CloneDomainCheckerService import CloneDomainChecker
import os
import random
from termcolor import colored
import pyfiglet
from multiprocessing import Process, Manager
import logging

class dcc:
    def __init__(self):
        # Initialize the Main class
        self.logger = LoggingService(__name__).getLogger()
        self.config = ConfigService().config

        # Add a couple of blank lines before printing the ASCII art
        art = pyfiglet.figlet_format(self.config["appName"], width=200)
        color_choices = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']  # Add your desired colors
        chosen_color = random.choice(color_choices)
        colored_art = colored(art, chosen_color)
        self.logger.info("\n\n" + colored_art)

        # Set the output directory
        self.outputDir = "_output"

    def get_log_level(self):
        return getattr(logging, self.config.get("logLevel", "INFO").upper(), logging.INFO)

    def run(self, target_domain=None):
        if target_domain:
            self.logger.info("Domain specified via command line: " + target_domain)
            separator = '.'
            trimmed = target_domain.split(separator, 1)[0]
            target_domain = trimmed
            self.logger.info("Root: " + target_domain)

            # Overwrite base_strings in config.json with the specified target_domain
            config_file = os.path.join("config", "config.json")
            with open(config_file, 'r') as f:
                config_data = json.load(f)

            config_data['base_strings'] = [target_domain]

            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=4)

        config_file = os.path.join("config", "config.json")
        timestamp = time.strftime("%Y%m%d%H%M%S")
        output_file = os.path.join(self.outputDir, f"output_{timestamp}.log")
        self.checker = CloneDomainChecker(config_file, output_file, self.logger)        
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
if __name__ == "__main__":
    target_domain = None
    if len(sys.argv) > 1:
        target_domain = sys.argv[1]

    myApp = dcc()
    myApp.run(target_domain)
