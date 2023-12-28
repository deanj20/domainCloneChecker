# domainCloneChecker (with DNS Twist and WHOISJSON API)



**GETTING STARTED**
* --WINDOWS--
* Open VsCode
* Open terminal within VsCode
* `python --version`
* `python -m venv .venv`
* `.venv\scripts\activate `
* `pip3 install -r requirements.txt`
* `git submodule init`
* `git submodule update`


* --LINUX--
* Open Terminal
* Change to program path
* `python3 --version`
* `python3 -m venv .venv`
* `. .venv/bin/activate`
* `pip3 install -r requirements.txt`
*  `git submodule init`
* `git submodule update`



To save new packages:
* `pip freeze > requirements.txt`

**BRIEF SUMMARY**

 domainCloneChecker - this project began as a hobby / personal investigation Sprint 2023, then I re-purposed it for a 
 Computer Science Research Methods class I was taking for my masters Fall 2023.
 Along the way I discovered DNS Twist by Marcin Ulikowski which is lightyears beyond what I would have ever accomplished
 (Current build of DNS Twist is available at: https://github.com/elceef/dnstwist)
 
However, I was still finding some sites with DCC that DNS Twist was not, so I left it in.
 
The research paper will be added to this repo on completion.
 
I am not much of a programmer, but I had an idea about what I wanted to do, and made it work
 This code needs an overhaul which I may take on someday - see Future Improvements in Research Paper on attached
 Hopefully it will be helpful for someone curious like me.
 -JRD

##Standalone:

Any of these tools can be used stand alone. The walktrhough below is only for someone wanting to repeat the steps I completed
for my research paper - to build a sqlite database and export to CSV

**dntwist**

*   cd dnstwist
*   ./dnstwist.py -r example.com
*   #see https://github.com/elceef/dnstwist for full list of arguments.

**domainCloneChecker**
*   cd domainCloneChecker
*   ./dcc.py example.com
*   #or
*   #edit config/config.json with your TLDs and domain roots
*   #then run
*   python3 main.py

**checkWhoIs (with WHOISJSONAPI)**
*   cd domainCloneChecker/services
*   ./checkWhoIs/py example.com
*   #provide your own API key or this won't work
*   #end of file     access_token = "??????????????????????????????????????????????????????????"


## Walkthrough
These are the steps I followed for my research paper, 
"Proactive Detection of Impostor Domains for Improved Protection Against Spear Phishing Attacks"


1. Create a company csv file in this format and save it in this folder as filename.csv:

        Category,Business Name,Relationship,Website
        IT MSP,JDO Tek,self,jdotek.com
        News Media,ABC,affiliate,abc.com
        Tool Company,ACME,supplier,acme.com

    Note 1: Only use base domain. So if you want to check dps.texas.gov, add only texas.gov.
    
    Note 2: Avoid duplicate Website values - this can cause issues during DCC portion (step 4)


2. From this folder run the following command to build a sqlite database from the file. See README.md in the domainclonechecker folder if you need help installing a venv or sqlite3, etc. This will create a database and a single table with the same root name as your csv file

    `./create_sqlite_table.py filename.csv`
    (this creates a sqlite database called filename.db with a table called filename)


3. Now run the following script to run DNS Twist against the new database. The script will take the DNS Twist findings and insert them into the database. 

    `./passWithDNSTwist.py filename.db`

    Note 1: Depending on the number of sites in your CSV **this can take a very long time**. You may try a dry run from the dnstwist folder using ./dnstwist.py domainname to get an idea about how long it takes to complete. It will test hundreds if not thousands of permutations of each domain. The longer the name, the more permutations.

    Note 2: Short Domain Names (4 chars or fewer) tend to trigger a large amount of false positives in DNS Twist because it does adds/removals/replacements. So 3M.com would test for 3MS.com, DMS.com, 3.com, etc. etc. You can adjust the DNS Twist command being passed in the script, or simply filter out these high-rate false positive fuzzers in the final result. This isn't as much of an issue on longer domains.

    Note 3: I like to monitor the results in a second terminal with this command. It will launch a visual of the database in a srcollable format. Type q to refresh (it will refesh in 2 seconds. ctrl + C to exit): 

    `while true; do sqlite3 -column -header ./filename.db "SELECT * FROM filename;" | less; sleep 2; done`


4. On completion of step 3 the database will have all of the information found by DNS Twist. Now we will add in information from DomainCloneChecker (DCC). This is a two step process since DCC outputs results into log files for each site, and then we use a second script to parse the info into the database. 

    As with the other script, **this can take a very long time** to run depending on the number of entries and their characteristics. Last estimate: 4 mins/domain

    #move the .db file to the domainCLoneChecker folder (I will fix this eventually but for now it's simpler to just move it)
    `mv filename.db ./domainCloneChecker/`

    #now cd to the domainCloneChecker path, clear the output folder and run the script to run dcc against the db
    `cd domainCloneChecker`
    `rm -rf _output/*`
    `./bulkRunDcc.py filename.db`


5. Once DCC completes, run the following command to parse all the useful info from the logs and add it to the database. Note that DCC will not overwrite DNS Twist data, it will just update the time stamp for that row and mark TRUE under "found_by_dcc".

    `./bulkAppendDccData.sh filename.db`


6. Now all that is left is to pull Registrar info and append that to the database as well.

    `./UpdateWhoIsInfo.py filename.db`

    Note: This script uses an API call to whoisjsonapi.com which is free for up to 1000 calls a month. **You will need to sign up and use your own API access token in the script** - look near the bottom of the script UpdateWhoIsInfo.py. If you go over 1,000 requests you will receive the notice: HTTP Error: 429 Client Error: Too Many Requests for url: https://whoisjsonapi.com/v1/[somedomainstring]. You may choose to sign up for their unlimited plan for $40 a month, or re-write this script to use some other service. You cannot constantly query the default whois database on most systems without being blocked (i.e. if you run whois google.com in a loop, you will soon get warnings and no longer receive the requested info), which is why these bulk-check services exist for a fee. 


7. From here the database is complete. You can move the .db file anywhere you'd like, or export it to a CSV with the following command:

    `./exportCSV.sh filename.db`


8. The resulting CSV can be used for whatever purpose required - using the "discovered domain" column to feed blacklists might be an idea (be sure to remove any rows with *original fuzzer types first as those would be legitimate domains.) For my research I will be inserting it into PowerBI where I can make other conditional columns and graphs, etc, to gauge the effectiveness of tools like DNS Twist and DCC compared to traditional public blacklists, hueristics/AI detection and other methods.
