import csv
import subprocess
import re

# Path to the original CSV file
input_csv_path = 'exportFile.csv'
# Path to the new CSV file with additional Whois information
output_csv_path = 'exportFile_with_whois.csv'
"""
def get_whois_dates(domain):
    # Run the checkWhoIs.py script and capture the output
    result = subprocess.run(['./checkWhoIs.py', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


    
    # Check if the command was successful
    if result.returncode == 0:
        # Split the output into lines
        lines = result.stdout.split('\n')
        # Extract relevant date fields
        created_date = lines[13].split(':')[1].strip()
        updated_date = lines[15].split(':')[1].strip()
        expiration_date = lines[17].split(':')[1].strip()
        return created_date, updated_date, expiration_date
    else:
        print(f"Failed to retrieve Whois information for {domain}")
        return None, None, None
"""

def get_whois_dates(domain):
    # Run the checkWhoIs.py script and capture the output
    print(f"Checking {domain}")
    result = subprocess.run(['./checkWhoIs.py', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    # Check if the command was successful
    if result.returncode == 0:
        # Split the output into lines
        lines = result.stdout.split('\n')

        # Extract relevant date fields
        """     
        created_date = next(line.split(': ')[1].strip() for line in lines if line.startswith('  created_date_in_time:'))
        updated_date = next(line.split(': ')[1].strip() for line in lines if line.startswith('  updated_date_in_time:'))
        expiration_date = next(line.split(': ')[1].strip() for line in lines if line.startswith('  expiration_date_in_time:'))
        """     
        created_date_line = next((line for line in lines if line.startswith('  created_date_in_time:')), None)
        updated_date_line = next((line for line in lines if line.startswith('  updated_date_in_time:')), None)
        expiration_date_line = next((line for line in lines if line.startswith('  expiration_date_in_time:')), None)

        created_date = created_date_line.split(': ')[1].strip() if created_date_line else None
        updated_date = updated_date_line.split(': ')[1].strip() if updated_date_line else None
        expiration_date = expiration_date_line.split(': ')[1].strip() if expiration_date_line else None

        return created_date, updated_date, expiration_date
    else:
        print(f"Failed to retrieve Whois information for {domain}")
        return None, None, None

def update_csv(input_csv_path, output_csv_path):
    # Open the original CSV file for reading
    with open(input_csv_path, 'r') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['created_date_in_time', 'updated_date_in_time', 'expiration_date_in_time']

        # Open a new CSV file for writing
        with open(output_csv_path, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            # Iterate through each row in the original CSV
            for row in reader:
                domain = row['domain']
                # Get Whois dates
                created_date, updated_date, expiration_date = get_whois_dates(domain)

                # Update the row with Whois dates
                row['created_date_in_time'] = created_date
                row['updated_date_in_time'] = updated_date
                row['expiration_date_in_time'] = expiration_date

                # Write the updated row to the new CSV file
                writer.writerow(row)

if __name__ == "__main__":
    update_csv(input_csv_path, output_csv_path)
    print(f"Updated CSV file saved to {output_csv_path}")
