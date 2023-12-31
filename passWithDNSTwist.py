#!/usr/bin/env python

import sqlite3
import subprocess
import csv
from io import StringIO
import time
import sys

def update_or_insert_row(conn, row, dnstwist_result, table_name):
    cursor = conn.cursor()

    # Check if the necessary columns exist, and add them if not
    required_columns = ["Business Name", "Website", "Relationship", "Category", "fuzzer", "discovered domain", "dns_a", "dns_aaaa", "dns_mx", "dns_ns", "found by dns_twist", "last db update"]
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [column[1] for column in cursor.fetchall()]

    for column in required_columns:
        if column not in existing_columns:
            cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN "{column}" TEXT')

    legitimate_domain = row[3]

    # Now proceed with the rest of the function
    cleaned_legitimate_domain = legitimate_domain.replace("http://", "").replace("https://", "")
    discovered_domain = dnstwist_result.get('domain', '')

    # Check if the domain already exists in the database
    cursor.execute(f'SELECT * FROM {table_name} WHERE "Website" = ?', (discovered_domain,))
    existing_row = cursor.fetchone()

    if existing_row:
        # Domain exists, perform an UPDATE
        cursor.execute(f'UPDATE {table_name} SET fuzzer = ?, "discovered domain" = ?, dns_a = ?, dns_ns = ?, "found by dns_twist" = ?, "last db update" = ? WHERE "Website" = ?',
                    (dnstwist_result.get('fuzzer', ''), discovered_domain,
                        dnstwist_result.get('dns_a', ''), dnstwist_result.get('dns_ns', ''), "TRUE", time.strftime('%Y-%m-%d %H:%M:%S'), discovered_domain))
    else:
        # Domain does not exist, perform an INSERT
        cursor.execute(f'INSERT INTO {table_name} ("Business Name", "Website", "Relationship", "Category", fuzzer, "discovered domain", dns_a, dns_aaaa, dns_mx, dns_ns, "found by dns_twist", "last db update") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (row[2], row[4], row[3], row[1],  
                        dnstwist_result.get('fuzzer', ''), discovered_domain, dnstwist_result.get('dns_a', ''),
                        dnstwist_result.get('dns_aaaa', ''), dnstwist_result.get('dns_mx', ''), dnstwist_result.get('dns_ns', ), "TRUE", time.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./script_name.py <database_name>")
        sys.exit(1)

    database_name = sys.argv[1]
    table_name = database_name[:-3]

    conn = sqlite3.connect(f'{database_name}')

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    for row in rows:
        print(f"Checking domain: ", row[4])
        dnstwist_output = subprocess.check_output(['./dnstwist/dnstwist.py', '--format', 'csv', '--registered', row[4]])
        
        # Print DNSTwist output to the screen
        print("DNSTwist Output:")
        print(dnstwist_output.decode('utf-8'))

        dnstwist_csv = csv.DictReader(StringIO(dnstwist_output.decode('utf-8')))
        dnstwist_results = list(dnstwist_csv)

        for dnstwist_result in dnstwist_results:
            update_or_insert_row(conn, row, dnstwist_result, table_name)

    conn.close()
