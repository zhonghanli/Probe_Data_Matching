import csv
import os
import utm
import numpy as np
import numpy.linalg as linalg
from math import *
import pickle


class Probe():
    def __init__(self,row): 
        self.ID = row[0]
        self.dateTime = row[1]
        self.sourceCode = row[2]
        self.lat = float(row[3])
        self.lon = float(row[4])
        self.altitude = float(row[5])
        self.speed = float(row[6])
        self.heading = float(row[7])
        self.distance = 0
        self.potential_links = []
        self.coordinates = np.array([float(row[4])])

    def utm_coords(self):
        x, y, z, u = utm.from_latlon(self.lat, self.lon)
        return x,y

class Link():
    def __init__(self,row):
        self.PVID = row[0]
        self.direction= row[5]
        self.shapeInfo = row[14]
        self.slopeInfo = row[16]

    def get_segments(self):
        split_points = self.shapeInfo.split('|')
        points = []
        for i in split_points:
            split_ll = i.split('/')
            x, y, z, u = utm.from_latlon(float(split_ll[0]), float(split_ll[1]))
            points.append([x,y])
        segs = []
        for i in range(1, len(points)):
            segs.append([points[i-1], points[i]])
        return segs

    def calc_distance(self, dist, targetNode):
        split_points = self.shapeInfo.split('|')
        points = []
        for i in split_points:
            split_ll = i.split('/')
            x, y, z, u = utm.from_latlon(float(split_ll[0]), float(split_ll[1]))
            points.append([x,y])
        segs = []
        ret = dist
        if(len(segs)==2):
            return ret
        else:
            for i in range(1, len(segs)):
                if targetNode != segs[i]:
                    x1 = segs[i-1][0]
                    y1 = segs[i-1][1]
                    x2 = segs[i][0]
                    y2 = segs[i][1]
                    ret += sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
        return ret




def extractProbesAndLinks():
    probes = []
    with open('TopTenProbes.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            probe = Probe(row) 
            probes.append(probe)

    links = []
    with open("../probe_data_map_matching/LinkData_processed.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            link = Link(row)
            links.append(link)
    
    return probes, links

#l1 -> l2 is link, p is probe location
###https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
def calcDist(l1, l2, p):
    x1, y1 = l1[0], l1[1]
    x2, y2 = l2[0], l2[1]
    x3, y3 = p[0], p[1]

    px = x2-x1
    py = y2-y1
    norm = px*px + py*py
    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(norm)
    if u > 1:
        u = 1
    elif u < 0:
        u = 0
    x = x1 + u * px
    y = y1 + u * py
    dx = x - x3
    dy = y - y3
    dist = (dx*dx + dy*dy)**.5
    return dist, [x,y]

def findClosestLine(probe, mapped_segments):
    min_dist = 20
    closest = []
    x,y = probe.utm_coords()
    for i in mapped_segments:
        dist, projection = calcDist(i[0], i[1], [x,y])
        if dist < 20:
            diff = probe.heading - angle(i[0], i[1])
            if abs(diff) < 45 or 135 < abs(diff) < 225:
                if dist < min_dist:
                    min_dist = dist
                    i.append(sqrt( (projection[0] - i[0][0])**2 + (projection[1] - i[0][1])**2 )) #dist from segment ref
                    i.append(sqrt( (projection[0] - x)**2 + (projection[1] - y)**2 )) #probe point to map-matched probe point distance
                    closest = i #includes pvid
    return closest

def angle(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    diff = y2-y1
    X = cos(x2)*sin(diff)
    Y = cos(x1)*sin(x2)-sin(x1)*cos(x2)*cos(diff)
    return degrees(atan2(X, Y))%360

def map_probes():
    print("Extracting probes and links...")
    probes, links = extractProbesAndLinks()

    print("Segmenting link shape...")
    link_segments = []
    for i in links:
        for j in i.get_segments():
            j.append(i.PVID)
            link_segments.append(j)

    print("Mapping...")

    rows = []
    counter = 0
    for i in probes:
        print(counter)
        counter +=1
        match = findClosestLine(i, link_segments)
        if match != []:
            row = []
            row.append(i.ID)
            row.append(i.dateTime)
            row.append(i.sourceCode)
            row.append(i.lat)
            row.append(i.lon)
            row.append(i.altitude)
            row.append(i.speed)
            row.append(i.heading)
            matchedLinkPVID = match[2]
            row.append(matchedLinkPVID)

            matched_link = []
            for j in links:
                if matchedLinkPVID == j.PVID:
                    matched_link=j
            if matched_link == []:
                print("Didn't find link matching that PVID")

            if abs(i.heading - angle(match[0], match[1])) < 90:
                row.append('F') if matched_link.direction == 'B' else row.append(matched_link.direction)
            else:
                row.append('T') if matched_link.direction == 'B' else row.append(matched_link.direction)
            
            #takes in distance and second node in segment
            row.append(matched_link.calc_distance(match[3], match[1]))
            row.append(match[4])
            rows.append(row)
    with open("matched_probes.csv", "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for row in rows:
            writer.writerow(row)
    # with open('mapped_probes1.pkl', 'wb') as f:
    #     pickle.dump(mapped, f)  

map_probes()

# with open('mapped_probes.pkl', 'rb') as f:
#     mynewlist = pickle.load(f)
#     for i in mynewlist:
#         print(i)














