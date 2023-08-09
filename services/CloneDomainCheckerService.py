import itertools
from datetime import datetime
import pydig
import logging
import os
import json
import socket

class CloneDomainChecker:
    def __init__(self, configFile, outputFile, logger):
        self.configFile = configFile
        self.outputFile = outputFile
        self.checked = []
        self.substitutions = {}
        self.suffixes = []
        self.verification_counts = {}
        self.logger = logger

    def load_base_strings(self):
        with open(self.configFile, 'r') as config_file:
            config_data = json.load(config_file)
            return config_data.get('base_strings', [])

    def load_substitutions(self):
        with open(self.configFile, 'r') as config_file:
            config_data = json.load(config_file)
            return config_data.get('substitutions', {})

    def load_suffixes(self):
        with open(self.configFile, 'r') as config_file:
            config_data = json.load(config_file)
            return config_data.get('suffixes', [])

    def run(self):
        self.tests = self.load_base_strings()
        self.substitutions = self.load_substitutions()
        self.suffixes = self.load_suffixes()
        total_elements = self.get_total_elements()

        self.logger.info("Number of base strings to check: " + str(len(self.tests)))
        self.logger.info("Number of char substitutions coded: " + str(len(self.substitutions)))
        self.logger.info("Number of possibilities for char substitutions coded: " + str(total_elements))

        for x in self.tests:
            self.generate_2_deep(x)

        ct = datetime.now()
        ct = str(ct)
        with open(self.outputFile, "a") as file1:  # append mode
            file1.write("\n\nTimeStamp: " + ct)
            file1.write("\n############# END OF RUN #############\n")
            file1.write("\n\nSites found: ")
            if self.checked:
                file1.write(str(self.checked))
            else:
                file1.write("No sites found")

        self.logger.info("End of Run. Sites found:")
        self.logger.info(self.checked)

    def generate_substitutions(self, word):
        yield word
        for i in range(len(word)):
            if word[i].lower() in self.substitutions:
                for sub in self.substitutions[word[i].lower()]:
                    yield word[:i] + sub + word[i + 1:]

    def generate_combinations(self, word):
        for i in range(len(word) + 1):
            for subset in itertools.combinations(range(len(word)), i):
                combo = ''.join(word[j] if j not in subset else 'xxx' for j in range(len(word)))
                if 'xxx' not in combo:
                    yield combo

    def generate_urls(self, word):
        all_combinations = list(self.generate_combinations(word))
        all_substitutions = list(self.generate_substitutions(word))
        for combo in all_combinations:
            for sub in all_substitutions:
                for suffix in self.suffixes:
                    url = sub + suffix
                    if ((".." not in url) and ("xxx" not in url) and (url not in self.checked)):
                        yield url

    def check_and_add_positive(self, domain):
        if self.check_domain(domain):
            if domain not in self.verification_counts:
                self.verification_counts[domain] = 1
            else:
                self.verification_counts[domain] += 1
            if self.verification_counts[domain] == 3:
                self.logger.info(domain + "--found")
                ct = datetime.now()
                ct = str(ct)
                with open(self.outputFile, "a") as file1:  # append mode
                    file1.write("\n\nTimeStamp: " + ct)
                    file1.write("\nDomain found: " + domain + " - Verified 3 times")

    def generate_2_deep(self, word):
        for url in self.generate_urls(word):
            if ((".." not in url) and ("xxx" not in url) and (url not in self.checked)):
                if url != word:
                    self.check_and_add_positive(url)

    def check_domain(self, domain):
        try:
            a_records = pydig.query(domain, 'A')
            for record in a_records:
                self.logger.debug(f"{domain} --found (A record): {record}")
                self.checked.append(domain)
                return True

            aaaa_records = pydig.query(domain, 'AAAA')
            for record in aaaa_records:
                self.logger.debug(f"{domain} --found (AAAA record): {record}")
                self.checked.append(domain)
                return True

            mx_records = pydig.query(domain, 'MX')
            for record in mx_records:
                self.logger.debug(f"{domain} --found (MX record): {record}")
                self.checked.append(domain)
                return True

            auth_answers = pydig.query(domain, 'SOA')
            for record in auth_answers:
                self.logger.debug(f"{domain} --found (Authoritative answers): {record}")
                self.checked.append(domain)
                return True

            self.logger.debug(f"{domain} --not found")
            return False
        except Exception as e:
            self.logger.debug("[Transform URL - inner loop] EXCEPTION THROWN on " + domain + " - " + str(e))
            return False

    def get_total_elements(self):
        total_elements = 0
        total_elements += 1
        for character in self.substitutions:
            total_elements += len(self.substitutions[character])
        for character1, character2 in itertools.combinations(self.substitutions.keys(), 2):
            total_elements += len(self.substitutions[character1]) * len(self.substitutions[character2])
        return total_elements
