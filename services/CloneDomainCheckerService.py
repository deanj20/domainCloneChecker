# CloneDomainCheckerService.py

import itertools
from datetime import datetime
import pydig


class CloneDomainChecker:
    def __init__(self, tests, outputFile):
        self.tests = tests
        self.outputFile = outputFile
        self.checked = []
        self.substitutions = {
            '1': ['i', 'l'],
            '2': ['s', 'z'],
            '3': ['e'],
            '4': ['a'],
            '5': ['s', 'z'],
            '6': ['g'],
            '7': ['t'],
            '8': ['b'],
            '9': ['p'],
            '0': ['0'],
            'a': ['4'],
            'b': ['8'],
            'd': ['cl'],
            'e': ['3'],
            'g': ['6', '9'],
            'i': ['1', 'l'],
            'l': ['1', 'i'],
            'm': ['nn'],
            'o': ['0'],
            'p': ['9'],
            'q': ['g'],
            's': ['5', 'z'],
            't': ['7'],
            'w': ['vv'],
            'z': ['2', 's']
        }

    def run(self):
        total_elements = 0

        print("Number of base strings to check: " + str(len(self.tests)))
        print("Number of char substitutions coded: " + str(len(self.substitutions)))
        for arr in self.substitutions:
            for items in self.substitutions[arr]:
                total_elements += 1
        print("Number of possibilities for char substitutions coded: " + str(total_elements))
        print("")

        for x in self.tests:
            self.process_orig_urls(x)
            self.generate_2_deep(x)

        ct = datetime.now()
        ct = str(ct)
        file1 = open(self.outputFile, "a")  # append mode
        file1.write("\n\nTimeStamp: " + ct)
        file1.write("\n############# END OF RUN #############\n")
        file1.write("\n\nSites found: ")
        file1.write(str(self.checked))
        file1.close()
        print("End of Run. Sites found:")
        print(self.checked)

    def generate_substitutions(self, word):
        for i in range(len(word)):
            if word[i].lower() in self.substitutions:
                for sub in self.substitutions[word[i].lower()]:
                    yield word[:i] + sub + word[i + 1:]

    def generate_combinations(self, word):
        for i in range(len(word) + 1):
            for subset in itertools.combinations(range(len(word)), i):
                yield ''.join(word[j] if j not in subset else 'xxx' for j in range(len(word)))

    def generate_urls(self, word):
        for combo in self.generate_combinations(word):
            for sub in self.generate_substitutions(combo):
                for suffix in [".net", ".com", ".org", ".edu", ".io", ".tv", ".co", ".biz"]:
                    yield sub + suffix

    def process_orig_urls(self, word):
        for suffix in [".net", ".com", ".org", ".edu", ".io", ".tv", ".co", ".biz"]:
            url = (word + suffix)
            if ((".." not in url) and ("xxx" not in url) and (url not in self.checked)):
                print("Checking " + url)
                whois_result = pydig.query(url, 'NS')
                if len(whois_result) > 0:
                    ct = datetime.now()
                    ct = str(ct)
                    file1 = open(self.outputFile, "a")  # append mode
                    file1.write("\n\nTimeStamp: " + ct)
                    file1.write("\nDomain found: " + url + " - Entries: " + str(len(whois_result)))
                    file1.write(str(whois_result))
                    file1.close()
                    self.checked.append(url)
                    print(self.checked)
                else:
                    print("[Transform URL - outer loop] NO MATCH OR SKIPPED: " + url +
                          ". URL in checked list: " + str(url in self.checked))

    def generate_2_deep(self, word):
        for url in self.generate_urls(word):
            if ((".." not in url) and ("xxx" not in url) and (url not in self.checked)):
                if url != word:
                    print("Checking " + url)
                    whois_result = pydig.query(url, 'NS')
                    print(len(whois_result))
                    if len(whois_result) > 0:
                        ct = datetime.now()
                        ct = str(ct)
                        file1 = open(self.outputFile, "a")  # append mode
                        file1.write("\n\nTimeStamp: " + ct)
                        file1.write("\nDomain found: " + url + " - Entries: " + str(len(whois_result)))
                        file1.write(str(whois_result))
                        file1.close()
                        self.checked.append(url)
