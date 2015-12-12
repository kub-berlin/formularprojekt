import json
import sys


f = lambda row: row['content'].encode('utf8')

if __name__ == '__main__':
    with open(sys.argv[1]) as fh:
        data = json.load(fh)

    odata = {f(row): f(row) for row in data['rows'] if row['content']}

    with open(sys.argv[2], 'w') as fh:
        json.dump(odata, fh, indent=2, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
