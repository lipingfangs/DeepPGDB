import csv
import sys
def round_value(value):
    try:
        return round(float(value), 2)
    except ValueError:
        return value

with open(sys.argv[1], 'r') as infile, open('output.csv', 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        rounded_row = [round_value(cell) for cell in row]
        writer.writerow(rounded_row)
