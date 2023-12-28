#!/usr/bin/env python3
import re
import sys
import sqlite3
from datetime import datetime


def get_table_name(db_file):
    return db_file.replace(".db", "")


def add_found_by_dcc_column(db_file):
    table_name = get_table_name(db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Check if the column exists
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    found_by_dcc_exists = any(column[1] == 'found_by_dcc' for column in columns)

    # If not, add the column
    if not found_by_dcc_exists:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN found_by_dcc BOOLEAN")

    conn.commit()
    conn.close()


def find_original_values(db_file, original_domain):
    table_name = get_table_name(db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Find the row with the *original domain
    cursor.execute(f'SELECT * FROM {table_name} WHERE "discovered domain" = ? AND fuzzer LIKE ?',
                   (original_domain, '%*original%'))
    original_row = cursor.fetchone()

    conn.close()

    return original_row


def parse_log(log_content):
    lines = log_content.split('\n')

    results = {}
    current_domain = None
    original_domain = None

    for line in lines:
        if not line or line.startswith('#') or line.startswith('Sites found:') or line.startswith('TimeStamp:'):
            continue

        if ':' in line:
            parts = line.split(':', 1)  # Split only at the first colon
            current_domain = parts[0].strip()

            if '*original' in line:
                original_domain = current_domain

            results[current_domain] = {
                "dns_a": [],
                "dns_aaaa": [],
                "dns_mx": [],
                "dns_ns": [],
            }

            if ',' in parts[1]:
                record_parts = parts[1].split(',', 3)  # Split only at the first three commas

                if len(record_parts) > 0:
                    dns_a = record_parts[0].replace("A Record:", "").replace(',', '').strip()
                    results[current_domain]["dns_a"] = ''.join(dns_a)

                if len(record_parts) > 1:
                    dns_aaaa = record_parts[1].replace("AAAA Record:", "").replace(',', '').strip()
                    results[current_domain]["dns_aaaa"] = dns_aaaa.split()

                if len(record_parts) > 2:
                    dns_mx = record_parts[2].replace("MX Record:", "").replace(',', '').strip()
                    results[current_domain]["dns_mx"] = dns_mx.split()

                if len(record_parts) > 3:
                    dns_ns = record_parts[3].replace("SOA Record:", "").replace(',', '').strip()
                    results[current_domain]["dns_ns"] = dns_ns.split()

    # Store original values for future use
    if original_domain and 'original' in results:
        original_values = find_original_values(sys.argv[1], original_domain)
        if original_values:
            results['original'] = {
                "Category": original_values[1],
                "Business Name": original_values[2],
                "Relationship": original_values[3],
                "Website": original_values[4],
            }

    return results



def fetch_original_values(db_file, domains):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Fetch values from the original row for the specified domains
    cursor.execute(f'SELECT * FROM {get_table_name(db_file)} WHERE fuzzer LIKE "%*original%" AND "discovered domain" IN ({",".join(["?"] * len(domains))})', domains)
    original_rows = cursor.fetchall()

    conn.close()

    return original_rows



def insert_into_db(db_file, results):
    table_name = get_table_name(db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # ... (previous code)

    # Fetch original values once
    original_values = fetch_original_values(db_file, list(results.keys()))  # Convert keys to list

    for domain, data in results.items():
        if '*original' in data.get('fuzzer', ''):
            continue  # Skip the '*original' key

        # Check if the row already exists
        cursor.execute(f'SELECT * FROM {table_name} WHERE "discovered domain" = ?', (domain,))
        existing_row = cursor.fetchone()

        if existing_row:
            print(f"Updating row for domain: {domain}")
            try:
                cursor.execute(
                    f'UPDATE {table_name} SET found_by_dcc = ?, "last db update" = ? WHERE "discovered domain" = ?',
                    ('TRUE', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), domain)
                )
            except sqlite3.Error as e:
                print(f'Error updating row for domain {domain}: {e}')
        else:
            print(f"Inserting new row for domain: {domain}")
            try:
                if original_values:
                    cursor.execute(
                        f'INSERT INTO {table_name} ("discovered domain", dns_a, dns_aaaa, dns_mx, dns_ns, found_by_dcc, fuzzer, "last db update", Category, "Business Name", Relationship, Website) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (domain, ''.join(data['dns_a']), ''.join(data['dns_aaaa']), ''.join(data['dns_mx']),
                         ''.join(data['dns_ns']), 'TRUE', 'dcc homoglyph', datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         original_values[0][1], original_values[0][2], original_values[0][3], original_values[0][4])
                    )
                else:
                    cursor.execute(
                        f'INSERT INTO {table_name} ("discovered domain", dns_a, dns_aaaa, dns_mx, dns_ns, found_by_dcc, fuzzer, "last db update") VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                        (domain, ''.join(data['dns_a']), ''.join(data['dns_aaaa']), ''.join(data['dns_mx']),
                         ''.join(data['dns_ns']), 'TRUE', 'dcc homoglyph', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    )
            except sqlite3.Error as e:
                print(f'Error inserting row for domain {domain}: {e}')

    conn.commit()
    conn.close()









def main():
    if len(sys.argv) != 3:
        print("Usage: ./appendDccData.py <database_file.db> <log_file.log>")
        sys.exit(1)

    db_file = sys.argv[1]
    log_file = sys.argv[2]

    with open(log_file, 'r') as file:
        log_content = file.read()

    add_found_by_dcc_column(db_file)  # Add the new column if it doesn't exist

    results = parse_log(log_content)
    insert_into_db(db_file, results)

    print("Data inserted and updated successfully!")


if __name__ == "__main__":
    main()
