# CloneDomainCheckerService.py
import itertools
from datetime import datetime
from itertools import combinations
import pydig
import json
import time
import sys
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet


# Download NLTK punkt resources if not already downloaded
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('words')
nltk.download('omw-1.4')


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
            base_strings = config_data.get('base_strings', [])            
            #self.logger.info("Grabbed Base Strings from config data" + str(base_strings))
            expanded_base_strings = []
            for word in base_strings:
                #self.logger.info("Finding root words" + str(base_strings))
                root_words = self.find_root_words(word)
                #self.logger.info("Adding root words strings to final base strings list" + str(base_strings))
                expanded_base_strings.extend(root_words)

            return expanded_base_strings


    def find_root_words(self, word):
        root_words = [word]
        min_word_length = 3
        max_word_length = len(word)

        for i in range(min_word_length, min(len(word), max_word_length)):
            #self.logger.info("Checking word. root_words = " + str(root_words))
            ##self.logger.info("In Find Root Words Outer loop, min length of main string" + len(word))
            temp_list = []
            
            for j in range(0, len(word), max_word_length):
                current_combination = word[j:j + i]
                #self.logger.info("Testing current_combination = word[j:j + i]=" + str(current_combination))
                if current_combination.lower() in nltk.corpus.words.words():
                    current_remaining_combination = word[len(current_combination):len(word)]
                    #self.logger.info("Testing current_remaining_combination = word[len(current_combination):len(word)] = " + str(current_remaining_combination))
                    firstWordPass=False
                    secondWordPass=False
                    #if ((len(current_remaining_combination)>min_word_length)&(current_remaining_combination.lower() in nltk.corpus.words.words())):
                    #self.logger.info("We have a potential combo------------------------------------"+ "i=" + str(i) + "j=" + str(j) + current_combination.lower() + " and " + current_remaining_combination.lower())    
                    testWord = current_combination.lower()+'s'
                    #self.logger.info("Check Front Word:"+testWord)
                    #if (testWord in nltk.corpus.words.words()):
                    if(wordnet.synsets(testWord)):
                        firstWordPass=True
                        #self.logger.info("Pass:"+testWord)
                        #self.logger.info("found valid------------------------------------"+testWord)
                        plural = testWord+current_remaining_combination.lower()
                        hyphen_plural = testWord+'-'+current_remaining_combination.lower()
                        root_words.extend([plural,hyphen_plural])                                                    
                    testWord = current_remaining_combination.lower()+'s'
                    #self.logger.info("Check Back Word:"+testWord)
                    #if (testWord in nltk.corpus.words.words()):
                    if(wordnet.synsets(testWord)):                            
                        secondWordPass=True
                        #self.logger.info("Pass:"+testWord)
                        #self.logger.info("found valid------------------------------------"+testWord)
                        plural = current_combination.lower()+testWord
                        hyphen_plural = current_combination.lower()+'-'+testWord
                        root_words.extend([plural,hyphen_plural])                                                                                                   
                    #if ((current_combination.lower()+'s' in nltk.corpus.words.words())&(current_remaining_combination.lower()+'s' in nltk.corpus.words.words())):
                    if(firstWordPass & secondWordPass):                            
                        #self.logger.info("found valid------------------------------------"+current_combination.lower()+'s'+'-'+current_remaining_combination.lower()+'s')
                        plural = current_combination.lower()+'s'+current_remaining_combination.lower()+'s'
                        hyphen_plural = current_combination.lower()+'s-'+current_remaining_combination.lower()+'s'
                        root_words.extend([plural,hyphen_plural])    
        return root_words



    def load_substitutions(self):
        with open(self.configFile, 'r') as config_file:
            config_data = json.load(config_file)
            return config_data.get('substitutions', {})

    def load_suffixes(self):
        with open(self.configFile, 'r') as config_file:
            config_data = json.load(config_file)
            return config_data.get('suffixes', [])

    def run(self):
        ct = datetime.now()
        ct = str(ct)
        with open(self.outputFile, "a") as file1:  # append mode
            file1.write("\n############# START OF RUN #############\n")
            file1.write("TimeStamp: " + ct + "\n")
        self.tests = self.load_base_strings()
        self.substitutions = self.load_substitutions()
        self.suffixes = self.load_suffixes()
        total_elements = self.get_total_elements()

        for x in self.tests:
            self.generate_2_deep(x)

        ct = datetime.now()
        ct = str(ct)
        with open(self.outputFile, "a") as file1:  # append mode
            file1.write("\n\nSites found: ")

            if self.checked:
                file1.write(str(self.checked))
                file1.write("\n\n")
            else:
                file1.write("No sites found")
            file1.write("\n\nTimeStamp: " + ct)
            file1.write("\n############# END OF RUN #############\n")

        sys.stdout.write("\r\033[1K")  # Clear from the beginning of the line

        #self.logger.info("\nEnd of Run. Sites found:")
        #self.logger.info(self.checked)

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
                #self.logger.info(domain + "--found")
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
            a_record_info = f"A Record: {', '.join(a_records)}" if a_records else ""

            aaaa_records = pydig.query(domain, 'AAAA')
            aaaa_record_info = f"AAAA Record: {', '.join(aaaa_records)}" if aaaa_records else ""

            mx_records = pydig.query(domain, 'MX')
            mx_record_info = f"MX Record: {', '.join(mx_records)}" if mx_records else ""

            auth_answers = pydig.query(domain, 'SOA')
            soa_record_info = f"SOA Record: {', '.join(auth_answers)}" if auth_answers else ""

            # Decide whether something was found
            found_something = any([a_records, aaaa_records, mx_records, auth_answers])

            if found_something:
                # Remove commas from the record information
                a_record_info = a_record_info.replace(",", "")
                aaaa_record_info = aaaa_record_info.replace(",", "")
                mx_record_info = mx_record_info.replace(",", "")
                soa_record_info = soa_record_info.replace(",", "")

                # Record the information to the output file
                with open(self.outputFile, "a") as file1:  # append mode
                    file1.write(f"\n{domain}: {a_record_info},{aaaa_record_info},{mx_record_info},{soa_record_info}\n")


                # Log the information to the console
                self.logger.debug(f"{domain} --found: {a_record_info} {aaaa_record_info} {mx_record_info} {soa_record_info}")

                self.checked.append(domain)
                return True
            else:
                # Simulate not found case with line overwriting
                message = f"\r{domain} --not found"
                buffer_size = max(len(message), 15)
                sys.stdout.write("\033[1K")  # Clear from the beginning of the line
                sys.stdout.write(message[:buffer_size] + " " * (buffer_size - len(message)))  # Pad with spaces
                sys.stdout.flush()
                time.sleep(0.1)
                return False

        except Exception as e:
            self.logger.debug(f"\r[Transform URL - inner loop] EXCEPTION THROWN on {domain} - {str(e)}")
            return False


    def colorize_output(self, domain):
        base_strings = self.load_base_strings()
        standard_suffixes = [".com", ".net", ".org", ".edu", ".gov"]

        if any(domain.endswith(suffix) for suffix in standard_suffixes) and any(base in domain for base in base_strings):
            return f"\033[1;32m{domain}\033[0m"  # Bright green for exact match and standard suffixes
        elif any(base in domain for base in base_strings):
            return f"\033[1;93m{domain}\033[0m"  # Bright yellow for exact match and non-standard suffixes
        else:
            return f"\033[1;91m{domain}\033[0m"  # Bright red for other cases

    def get_total_elements(self):
        total_elements = 0
        total_elements += 1
        for character in self.substitutions:
            total_elements += len(self.substitutions[character])
        for character1, character2 in itertools.combinations(self.substitutions.keys(), 2):
            total_elements += len(self.substitutions[character1]) * len(self.substitutions[character2])
        return total_elements
