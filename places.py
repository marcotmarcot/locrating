#!/usr/bin/python3

import json
import requests
import sys

schools = ''''''

def main():
    for school in schools.split('\n'):
        url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=' + school + ' London&inputtype=textquery&fields=rating&key=' + sys.argv[1]
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        js = json.loads(response.text)

        if js['status'] == 'ZERO_RESULTS':
            print(school + '\t')
            continue

        if js['status'] != 'OK':
            print(school + ': ' + str(js), file=sys.stderr)
            break

        candidate = js['candidates'][0]
        if 'rating' not in candidate:
            print(school + '\t')
            continue

        print(school + '\t' + str(candidate['rating']))


if __name__ == '__main__':
    main()
