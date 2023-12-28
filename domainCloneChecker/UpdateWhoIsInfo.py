#!/usr/bin/env python

import sys
import requests
import sqlite3

def colorize(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def get_whois_info(domain, access_token):
    url = f"https://whoisjsonapi.com/v1/{domain}"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Oops! Something went wrong:", err)
    return None

def print_colorized_info(info):
    if not info:
        return

    print("domain:")
    for key, value in info['domain'].items():
        if key in ['name_servers', 'created_date', 'name']:
            print(f"  {key}: {colorize(value, '93')}")
        else:
            print(f"  {key}: {value}")

    print("registrar:")
    registrar_info = info.get('registrar', {})
    for key, value in registrar_info.items():
        if key == 'name':
            print(f"  {key}: {colorize(value, '93')}")
        else:
            print(f"  {key}: {value}")

def update_database(cursor, domain, access_token, table_name):
    # Check if the table exists, if not, create it
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            "discovered domain" TEXT PRIMARY KEY,
            created_date TEXT,
            updated_date TEXT,
            expiration_date TEXT,
            status TEXT,
            registrar_id TEXT,
            registrar_name TEXT,
            registrar_email TEXT
        )
    """)

    # Check if the domain already exists in the table
    cursor.execute(f'SELECT * FROM {table_name} WHERE "discovered domain"=?', (domain,))
    existing_data = cursor.fetchone()

    if existing_data:
        # If the domain already exists, update the existing record
        print(f"Updating existing record for {domain}")
    else:
        # If the domain doesn't exist, insert a new record
        print(f"Inserting new record for {domain}")
        cursor.execute(f'INSERT INTO {table_name} ("discovered domain") VALUES (?)', (domain,))

    # Fetch WHOIS information
    whois_info = get_whois_info(domain, access_token)

    # Update the database with WHOIS information
    if whois_info:
        # Create missing columns if they don't exist
        for column in ["created_date", "updated_date", "expiration_date", "status", "registrar_id", "registrar_name", "registrar_email"]:
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = [col[1] for col in cursor.fetchall()]
            if column not in columns:
                cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column} TEXT')

        # Update the data in the database
        cursor.execute(f"""
            UPDATE {table_name} SET
            created_date=?,
            updated_date=?,
            expiration_date=?,
            status=?,
            registrar_id=?,
            registrar_name=?,
            registrar_email=?
            WHERE "discovered domain"=?
        """, (
            whois_info['domain'].get('created_date_in_time', ''),
            whois_info['domain'].get('updated_date_in_time', ''),
            whois_info['domain'].get('expiration_date_in_time', ''),
            ', '.join(whois_info['domain'].get('status', [])),
            whois_info.get('registrar', {}).get('id', ''),
            whois_info.get('registrar', {}).get('name', ''),
            whois_info.get('registrar', {}).get('email', ''),
            domain
        ))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./update_database.py <database_name>")
        sys.exit(1)

    database_name = sys.argv[1]
    table_name = database_name.replace('.db', '')  # Use database name as the table name
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Replace this with your logic to fetch URLs from the database
    cursor.execute(f'SELECT "discovered domain" FROM {table_name}')
    domains = cursor.fetchall()

    access_token = "sbLxbHSxwV-OTSGGi_pcnpkyVuDa2AyoAxYqgIgmdC2zIXX_iNCQwClrCn18nsj"  # Replace with your actual access token

    for domain in domains:
        update_database(cursor, domain[0], access_token, table_name)

    conn.commit()
    conn.close()
