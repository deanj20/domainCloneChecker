import itertools
import subprocess
from datetime import datetime
import pydig
import array

outputFile="imposterDomains.txt"

# Define the substitutions to be made
substitutions = {
    '1': ['i','l'],
    '2': ['s','z'],
    '3': ['e'],
    '4': ['a'],
    '5': ['s','z'],
    '6': ['g'],
    '7': ['t'],
    '8': ['b'],
    '9': ['p'],
    '0': ['0'],
    'a': ['4'],
    'b': ['8'],
    'd': ['cl'],
    'e': ['3'],    
    'g': ['6','9'],    
    'i': ['1','l'],
    'l': ['1','i'],
    'm': ['nn'],
    'o': ['0'],
    'p': ['9'],
    'q': ['g'],
    's': ['5','z'],
    't': ['7'],
    'w': ['vv'],
    'z': ['2','s']
}

checked = []





# Generate all possible substitutions
def generate_substitutions(word):
    for i in range(len(word)):
        if word[i].lower() in substitutions:
            for sub in substitutions[word[i].lower()]:
                yield word[:i] + sub + word[i+1:]

# Generate all possible combinations
def generate_combinations(word):
    for i in range(len(word)+1):
        for subset in itertools.combinations(range(len(word)), i):
            yield ''.join(word[j] if j not in subset else 'xxx' for j in range(len(word)))

# Generate all possible URLs
def generate_urls(word):
    for combo in generate_combinations(word):
        for sub in generate_substitutions(combo):
            for suffix in [".net", ".com", ".org", ".edu", ".io",".tv",".co",".biz"]:
                yield sub + suffix

#For Origs
def orig_urls(word):
    for suffix in [".net", ".com", ".org", ".edu", ".io",".tv",".co",".biz"]:
        url = (word + suffix)
        if ((".." not in url) and ("xxx" not in url) and (url not in checked)):
            print("Checking " + url)
            #whois_result = find_whois(url)
            whois_result = pydig.query(url, 'NS')
            #print(whois_result)
            print(len(whois_result))
            if(len(whois_result) > 0):
                #print(whois_result)
                ct = datetime.now()
                ct=str(ct)
                file1 = open(outputFile, "a")  # append mode
                file1.write("\n\nTimeStamp: " + ct)
                file1.write("\nDomain found: " + url + " - Entries: " + str(len(whois_result))) 
                file1.write(str(whois_result))
                file1.close()
                checked.append(url)
                print(checked)
            else:
                print("[For Origs] NO MATCH OR SKIPPED: " + url)                        


#Bring it together 2 deep
def generate_2_deep(word):
    for url in generate_urls(word):
        if ((".." not in url) and ("xxx" not in url) and (url not in checked)):
            #print(url)
            if(url != word):
                print("Checking " + url)
                #whois_result = find_whois(url)
                whois_result = pydig.query(url, 'NS')
                #print(whois_result)
                print(len(whois_result))
                if(len(whois_result) > 0):                    
                    ct = datetime.now()
                    ct=str(ct)
                    file1 = open(outputFile, "a")  # append mode
                    file1.write("\n\nTimeStamp: " + ct)
                    file1.write("\nDomain found: " + url + " - Entries: " + str(len(whois_result)))
                    file1.write(str(whois_result))  
                    file1.close()
                    checked.append(url)
                    print(checked)
                else:
                    print("[generate_2_deep outer] NO MATCH OR SKIPPED: " + url)                        

                url = url[:-4]
                for url in generate_urls(url):
                    if (("xxx" not in url) and (url not in checked)):
                        if(url != word):
                            print("Checking " + url)                    
                            #whois_result = find_whois(url)
                            whois_result = pydig.query(url, 'NS')
                            #print(whois_result)
                            if(len(whois_result) > 0):
                                #print(whois_result)
                                ct = datetime.now()
                                ct=str(ct)
                                file1 = open(outputFile, "a")  # append mode
                                file1.write("\n\nTimeStamp: " + ct)
                                file1.write("\nDomain found: " + url + " - Entries: " + str(len(whois_result))) 
                                file1.write(str(whois_result))
                                file1.close()
                                checked.append(url)
                                print(checked)
                            else:
                                print("[generate_2_deep inner] NO MATCH OR SKIPPED: " + url)                        
"""
                url = url[:-4] #URL truncated by 1
                for url in generate_urls(url):
                    if ((".." not in url) and ("xxx" not in url) and (url not in checked)):
                        if(url != word):
                            print("Checking " + url)                    
                            #whois_result = find_whois(url)
                            whois_result = pydig.query(url, 'NS')
                            #print(whois_result)
                            if(len(whois_result) > 0):
                                #print(whois_result)
                                ct = datetime.now()
                                ct=str(ct)
                                file1 = open(outputFile, "a")  # append mode
                                file1.write("\n\nTimeStamp: " + ct)
                                file1.write("\nDomain found: " + url + " - Entries: " + str(len(whois_result))) 
                                file1.write(str(whois_result))
                                file1.close()
                                checked.append(url)
                                print(checked)
                            else:
                                print("[truncated] NO MATCH OR SKIPPED: " + url)                                     
  """                  

# Put domain root here.   
#tests = ["christushealth","chritushealth","cristushealth","chritus-health","cristus-health","chritus-health","christ-ushealth","christ-us-health","christishealth","christis-health"]
#tests = ["stxbeef","stx-beef","s-t-x-beef","STXbeaf"]
#tests = ["reddit","read-it","readdit","red-dit","read-it"]
#tests = ["cnn","c-n-n"]
#tests = ["bestbuy","bestbuys","betsbuy","bets-buy","best-buy"]
tests = ["warriortank","warriorstank","warrior-tank","warriors-tank","warriertank","worriertank","worrier-tank","warriortankmfg","warriorstankmfg","warrriortankmfg","warriorrtankmfg","warriertankmfg","warriortankmfg1","warriortanksmfg"]


for x in tests:
    result = orig_urls(x)    
    result = generate_2_deep(x)
ct = datetime.now()
ct=str(ct)
file1 = open(outputFile, "a")  # append mode
file1.write("\n\nTimeStamp: " + ct)
file1.write("\n############# END OF RUN #############\n") 
file1.write("\n\nSites found: ")
file1.write(str(checked))
file1.close()
print("End of Run. Sites found:")    
print(checked)
