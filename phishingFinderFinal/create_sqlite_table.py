#!/usr/bin/env python

import pandas as pd
import sqlite3
import sys

def create_sqlite_table(csv_file):
    # Load CSV into a pandas DataFrame with inferred header names
    df = pd.read_csv(csv_file, header=0)

    # Extract table name from the CSV filename
    table_name = csv_file.split('.')[0]

    # Connect to SQLite database
    conn = sqlite3.connect(f"{table_name}.db")

    # Write the DataFrame to a table in the SQLite database
    df.to_sql(table_name, conn, index=True, if_exists='replace')

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./create_sqlite_table.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]
    create_sqlite_table(csv_file)
