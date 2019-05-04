import csv
import os
import utm
import numpy as np
import numpy.linalg as linalg
import math
import pickle

linkdatafile = "../probe_data_map_matching/Partition6467LinkData.csv"

width=600
height=1000
Color_screen=(49,150,100)
Color_line=(255,0,0)


def extractUTMPointsFromLink(row):
    shapeInfo = row[14]
    split_points = shapeInfo.split('|')
    points = []
    for i in split_points:
        split_ll = i.split('/')
        x, y, z, u = utm.from_latlon(float(split_ll[0]), float(split_ll[1]))
        points.append([x,y])
    return points

def extractLinks(): 
    lines = []
    with open(linkdatafile) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            lines.append([row[0], extractUTMPointsFromLink(row)])
    return lines

def map_lines_to_linkPVID(links):
    final_lines = []
    for line in links:
        linkPVID = line[0]
        points = line[1]
        for i in range(1, len(points)):
            final_lines.append([points[i-1], points[i], linkPVID])
    return final_lines

def extractProbePoints():
    probepoints = []
    with open('TopTenProbes.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            x, y, z, u = utm.from_latlon(float(row[3]), float(row[4]))
            probepoints.append([x,y, (row[0], row[1])])
    return probepoints

#l1 -> l2 is link, p is probe location
def calcDist(l1, l2, p):
    dist = 999999999
    if p[0] > max(l1[0], l2[0]) or p[1] > max(l1[1], l2[1]) or p[0] < min(l1[0], l2[0]) or p[0] > min(l1[1], l2[1]):
        dist = min(math.sqrt( (p[0] - l1[0])**2 + (p[1] - l1[1])**2 ), math.sqrt( (p[0] - l2[0])**2 + (p[1] - l2[1])**2 ))
    else:
        # dist = abs((p[0]-l2[0])*(l2[1]-l1[1]) - (l2[0]-l1[0])*(p[1]-l2[1])) / np.sqrt(np.square(p[0]-l1[0]) + np.square(p[1]-l2[1]))
        l1 = np.asarray(l1)
        l2 = np.asarray(l2)
        p = np.asarray(p)

        dist = linalg.norm(np.cross(l2-l1, l1-p))/linalg.norm(l2-l1)
    return dist

def findClosestLine(probe_data, final_lines):
    min_dist = 99999999999
    closest = []
    for i in final_lines:
        dist = calcDist(i[0], i[1], [probe_data[0], probe_data[1]])
        if dist < min_dist:
            min_dist = dist
            closest = i #includes pvid
    return closest

def map_probes():
    all_lines = map_lines_to_linkPVID(extractLinks())
    probes = extractProbePoints()
    mapped = []

    counter = 0
    for i in probes:
        print(counter)
        counter +=1
        mapped.append([i, findClosestLine(i, all_lines)])

    with open('mapped_probes.pkl', 'wb') as f:
        pickle.dump(mapped, f)  

with open('mapped_probes.pkl', 'rb') as f:
    mynewlist = pickle.load(f)
    for i in mynewlist:
        print(i[1][0])














