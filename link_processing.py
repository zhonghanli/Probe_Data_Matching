import csv
import os
import utm
import numpy as np
import numpy.linalg as linalg
from math import *
import pickle

filename = "../probe_data_map_matching/Partition6467LinkData.csv"

links = []

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        if row[16]:
            links.append(row)

with open("../probe_data_map_matching/LinkData_processed.csv", "wb") as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for line in links:
        writer.writerow(line)
            
