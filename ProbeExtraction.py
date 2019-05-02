import csv
import os

filename = "Partition6467ProbePoints.csv"
ids = ["21066","57433","4560","69121","21065","55101","18420","57278","35008","57283"]
data = []

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        if row[0] in ids:
            data.append(row)

with open("output", "wb") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for line in data:
        writer.writerow(line)

