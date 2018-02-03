import sys
import csv
import json


if __name__ == '__main__':
    with open(sys.argv[1]) as fh:
        data = json.load(fh)

    keys = []

    with open(sys.argv[2], 'w') as fh:
        w = csv.writer(fh, dialect='unix')
        for row in data['rows']:
            key = row.get('content')
            if key and key not in keys:
                keys.append(key)
                w.writerow((key, key))
