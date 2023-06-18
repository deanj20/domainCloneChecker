from itertools import product

def make_patterns(s):

    keyletters = 'a4'
    keyletters2 = '1il'
    keyletters3 = 'o0'
    keyletters4 = 't7'
    keyletters5 = 'g6'
    keyletters6 = 'a4g61ilo0t7g6'

    # Convert input string into a list so we can easily substitute letters
    seq = list(s)

    # Find indices of key letters in seq
    indices = [ i for i, c in enumerate(seq) if c in keyletters ]
    indices2 = [ i for i, c in enumerate(seq) if c in keyletters2 ]
    indices3 = [ i for i, c in enumerate(seq) if c in keyletters3 ]
    indices4 = [ i for i, c in enumerate(seq) if c in keyletters4 ]
    indices5 = [ i for i, c in enumerate(seq) if c in keyletters5 ]
    indices6 = [ i for i, c in enumerate(seq) if c in keyletters6 ]

    # Generate key letter combinations & place them into the list
    for t in product(keyletters, repeat=len(indices)):
        for i, c in zip(indices, t):
            seq[i] = c
        print(''.join(seq))


    # List 2
    for t in product(keyletters2, repeat=len(indices2)):
        for i, c in zip(indices2, t):
            seq[i] = c
        print(''.join(seq))


    # List 3
    for t in product(keyletters3, repeat=len(indices3)):
        for i, c in zip(indices3, t):
            seq[i] = c
        print(''.join(seq))


    # List 4
    for t in product(keyletters4, repeat=len(indices4)):
        for i, c in zip(indices4, t):
            seq[i] = c
        print(''.join(seq))


    # List 5
    for t in product(keyletters5, repeat=len(indices5)):
        for i, c in zip(indices5, t):
            seq[i] = c
        print(''.join(seq))        

    # List 6
    for t in product(keyletters6, repeat=len(indices6)):
        for i, c in zip(indices6, t):
            seq[i] = c
        print(''.join(seq))                

# Test

data = (
    'warriortankmfg',
    'warriorstankmfg',
    'warriortanksmfg',
    'warriorstanksmfg',
    'warrriortanksmfg',
    'warrriorstanksmfg',
    'warrriortankmfg',
    'warriortank',
    'warriortanks',
    'warriorstanks'
)

for s in data:
    print('\nInput:', s)
    make_patterns(s)