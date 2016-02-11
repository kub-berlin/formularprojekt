import sys
import json
import csv
import argparse

ensure_str = lambda s: s if isinstance(s, str) else s.encode('utf8')


def json2csv(fh):
    data = json.load(fh)
    encoded = [(ensure_str(a), ensure_str(b)) for a, b in data.items()]

    w = csv.writer(sys.stdout)
    w.writerows(encoded)


def csv2json(fh):
    r = csv.reader(fh)
    data = {}
    for row in r:
        key = row[0].decode('utf8')
        value = row[1].decode('utf8')
        data[key] = value
    s = json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
    print(ensure_str(s))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--reverse', '-r', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.path) as fh:
        if args.reverse:
            csv2json(fh)
        else:
            json2csv(fh)


if __name__ == '__main__':
    main()
