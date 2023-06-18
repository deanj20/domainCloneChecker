import itertools

# Define the substitutions to be made
substitutions = {
    'a': ['4'],
    'i': ['1','l'],
    'o': ['0'],
    's': ['5','z'],
    't': ['7'],
    'm': ['nn'],
    'g': ['6','9'],
    'e': ['3']    
}

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
            for suffix in [".net", ".com", ".org", ".edu"]:
                yield sub + suffix

#For Origs
def orig_urls(word):
    for suffix in [".net", ".com", ".org", ".edu"]:
                print(word + suffix)


#Bring it together 2 deep
def generate_2_deep(word):
    for url in generate_urls(word):
        if "xxx" not in url:
            print(url)
            url = url[:-4]
            for url in generate_urls(url):
                if "xxx" not in url:print(url)


# Test the function  
#tests = ["warriortankmfg","warriorstankmfg","warrriortankmfg","warriorrtankmfg","warriertankmfg","warriortankmfg1","warriortanksmfg"]
#tests = ["bestbuy","bestbuys","betsbuy","bets-buy","best-buy"]
tests = ["warriortank","warriorstank","warrior-tank","warriors-tank","warriertank","worriertank","worrier-tank"]
for x in tests:
    orig_urls(x)
    generate_2_deep(x)
