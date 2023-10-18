#!/usr/bin/env python

import sys
import requests

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
    for key, value in info['registrar'].items():
        if key == 'name':
            print(f"  {key}: {colorize(value, '93')}")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: checkWhoIs.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    access_token = "sbLxbHSxwV-OTSGGi_pcnpkyVuDa2AyoAxYqgIgmdC2zIXX_iNCQwClrCn18nsj"

    result = get_whois_info(domain, access_token)
    print_colorized_info(result)
