import csv
import sys

path = sys.argv[1]

with open(path, 'r') as fh:
    reader = csv.reader(fh)
    data = [(a, b) for a, b in reader if b != '']

with open(path, 'w') as fh:
    writer = csv.writer(fh, dialect='unix')
    for line in data:
        writer.writerow(line)
