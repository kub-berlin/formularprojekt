import json
import sys


ensure_str = lambda s: s if isinstance(s, str) else s.encode('utf8')
f = lambda row: ensure_str(row['content'])

if __name__ == '__main__':
    with open(sys.argv[1]) as fh:
        data = json.load(fh)

    odata = {f(row): f(row) for row in data['rows'] if row['content']}

    with open(sys.argv[2], 'w') as fh:
        json.dump(odata, fh, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
