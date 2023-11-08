#!/bin/bash

# Input CSV file
input_csv="ententPartners.csv"

# Output CSV file
output_csv="exportFile.csv"

# Remove existing output file if it exists
rm -f "$output_csv"

# Read the CSV file and iterate through each line
while IFS= read -r url; do
    echo "Processing $url..."

    # Extract the domain from the URL
    domain=$(echo $url | awk -F[/:] '{print $4}')

    # Run your Python program and append the results to the CSV file
    python3 ./dnstwist.py -r --format csv "$domain" | column -t -s, >> "$output_csv"

done < "$input_csv"

echo "Processing complete. Results saved to $output_csv"

