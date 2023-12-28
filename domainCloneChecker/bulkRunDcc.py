#!/usr/bin/env python3

import sys
import sqlite3
import subprocess
from subprocess import TimeoutExpired

def run_dcc(db_name):
    # Derive the table name from the database name
    table_name = db_name.replace('.db', '')

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Select rows where "fuzzer" is '*original'
    cursor.execute(f"SELECT Website FROM {table_name} WHERE fuzzer = '*original'")
    domains = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Iterate through the selected domains and call dcc.py for each
    for domain in domains:
        domain = domain[0]  # Extract the domain from the tuple

        try:
            # Set a 20-minute timeout
            subprocess.run(['./dcc.py', domain], timeout=1200)
        except TimeoutExpired:
            print(f"Timeout expired for domain {domain}. Moving on to the next.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./bulkRunDcc.py <database_name>")
        sys.exit(1)

    database_name = sys.argv[1]
    run_dcc(database_name)
