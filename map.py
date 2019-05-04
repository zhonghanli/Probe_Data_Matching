import csv
import os
import utm
import math
import pickle

import sys, pygame
from pygame.locals import*

filename = "../probe_data_map_matching/Partition6467LinkData.csv"

width=600
height=1000
Color_screen=(49,150,100)
Color_line=(255,0,0)

lines = []
probepoints = []

def extractUTMPointsFromLink(row):
    shapeInfo = row[14]
    split_points = shapeInfo.split('|')
    points = []
    for i in split_points:
        split_ll = i.split('/')
        x, y, z, u = utm.from_latlon(float(split_ll[0]), float(split_ll[1]))

        #scale
        y= int((y-5608275)/600)
        x=int((x-460213)/600)

        points.append([x,y])
    return points

def extractLines():
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            lines.append(extractUTMPointsFromLink(row))

def extractProbePoints():
    with open('TopTenProbes.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            x, y, z, u = utm.from_latlon(float(row[3]), float(row[4]))

             #scale
            y= int((y-5608275)/600)
            x= int((x-460213)/600)

            probepoints.append([x,y])

def scale(x,y):
    return (int((x-460213)/600), int((y-5608275)/600))

def drawLines(l, p):
    screen=pygame.display.set_mode((height,width))
    screen.fill(Color_screen)
    pygame.display.flip()

    for i in l:
        for j in range(1, len(i)):
            pygame.draw.line(screen,Color_line,(i[j-1][0],i[j-1][1]),(i[j][0],i[j][1]))

    for i in p:
        pygame.draw.circle(screen,(0,255,0), (i[0], i[1]), 1)
    
    with open('mapped_probes.pkl', 'rb') as f:
        mylist = pickle.load(f)
        for i in mylist:
            coords1 = scale(i[1][0][0], i[1][0][1])
            coords2 = scale(i[1][1][0], i[1][1][1])
            pygame.draw.line(screen,(0,0,255),coords1, coords2)


    pygame.display.flip()
    while True:
        for events in pygame.event.get():
            if events.type == QUIT:
                sys.exit(0)

def plotMap():
    extractLines()
    extractProbePoints()
    drawLines(lines, probepoints)

plotMap()










