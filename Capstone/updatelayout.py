from tkinter.tix import Tree
from procespool import Crate
from ast import Str
from typing import Dict, List
from unittest import skip
from xmlrpc.client import Boolean, boolean

from numpy import empty
from sqlalchemy import true
from item import Item
from binmanager import BinManager
import pandas as pd
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

crate_instances = []
binWidth = 34.9
binLength = 14.3
class Point:

    def __init__(self, xcoord=0, ycoord=0):
        self.x = xcoord
        self.y = ycoord

class Rect:
    def __init__(self, bottom_left, top_right, width, length, name: str):
        self.bottom_left = bottom_left
        self.top_right = top_right
        self.width = width
        self.length = length
        self.name = name

    def intersects(self, other):
        return not (self.top_right.x < other.bottom_left.x or self.bottom_left.x > other.top_right.x or self.top_right.y < other.bottom_left.y or self.bottom_left.y > other.top_right.y)


def loadCrate():
    df = pd.read_excel('Full tool list.xlsx')
    df = df[df['Occupied space'].notna()]
    colList = ["Occupied space", "Tool sqm", "Ailse", "Length", "Width", "Height", "Weights", "Crate Label", "Double stack"]
    dataColName = df.columns.tolist()
    indexList = []
    for colName in colList:
        indexList.append(dataColName.index(colName))
    crateInfoList = df.values.tolist()

    for crateInfo in crateInfoList:
        crate_instances.append(Crate(*[crateInfo[index] for index in indexList]))

    tracking_number = 1
    for crate in crate_instances:
        crate.set_tracking_number(str(tracking_number))
        tracking_number += 1

def addCrate(newCrate: Rect) -> bool:

    addSuccess = True

    if (newCrate.top_right.x > binWidth or newCrate.top_right.y > binLength) : addSuccess = False

    df_statistic = pd.read_csv("statistic.csv")
    trackingNumber = df_statistic['Crate'].tolist()
    Xaxis = df_statistic['X-axis'].tolist()
    Yaxis = df_statistic['Y-axis'].tolist()
    rotation = df_statistic['Rotation'].tolist()


    fig, ax = plt.subplots()
    ax.plot([0, 34.9],[0, 14.3], ls='')

    for index in range(len(trackingNumber)):
        getCrate = [crate for crate in crate_instances if crate.get_tracking_number() == trackingNumber[index]]
        if len(getCrate) > 0:
            if rotation[index] == False:
                compare = Rect(Point(Xaxis[index], Yaxis[index]), Point(Xaxis[index] + getCrate[0].width, Yaxis[index] + getCrate[0].length), getCrate[0].width, getCrate[0].length, str(getCrate[0].id))
                if (newCrate.intersects(compare)) : addSuccess = False
                ax.add_patch(Rectangle((Xaxis[index], Yaxis[index]), getCrate[0].width, getCrate[0].length, edgecolor = 'red',facecolor = 'white',fill=True))
            else:
                compare = Rect(Point(Xaxis[index], Yaxis[index]), Point(Xaxis[index] + getCrate[0].length, Yaxis[index] + getCrate[0].width), getCrate[0].length, getCrate[0].width, str(getCrate[0].id))
                if (newCrate.intersects(compare)) : addSuccess = False
                ax.add_patch(Rectangle((Xaxis[index], Yaxis[index]), getCrate[0].length, getCrate[0].width, edgecolor = 'red',facecolor = 'white',fill=True))
        else :
            exatTrankingNumber = trackingNumber[index].split(" x ")
            getStackCrate = [crate for crate in crate_instances if crate.get_tracking_number() == exatTrankingNumber[0]]
            if rotation[index] == False:
                compare = Rect(Point(Xaxis[index], Yaxis[index]), Point(Xaxis[index] + getStackCrate[0].width, Yaxis[index] + getStackCrate[0].length), getStackCrate[0].width, getStackCrate[0].length, str(getStackCrate[0].id))
                if (newCrate.intersects(compare)) : addSuccess = False
                ax.add_patch(Rectangle((Xaxis[index], Yaxis[index]), getStackCrate[0].width, getStackCrate[0].length, edgecolor = 'blue',facecolor = 'white',fill=True))
            else:
                compare = Rect(Point(Xaxis[index], Yaxis[index]), Point(Xaxis[index] + getStackCrate[0].length, Yaxis[index] + getStackCrate[0].width), getStackCrate[0].length, getStackCrate[0].width, str(getStackCrate[0].id))
                if (newCrate.intersects(compare)) : addSuccess = False
                ax.add_patch(Rectangle((Xaxis[index], Yaxis[index]), getStackCrate[0].length, getStackCrate[0].width, edgecolor = 'blue',facecolor = 'white',fill=True))
    
    
    ax.add_patch(Rectangle((newCrate.bottom_left.x, newCrate.bottom_left.y), newCrate.width, newCrate.length, edgecolor = 'purple',facecolor = 'purple',fill=True))
    plt.show()
    return addSuccess 

def updateCSV(crate: Rect):
    data = {
        'Crate': [crate.name],
        'X-axis': [crate.bottom_left.x],
        'Y-axis': [crate.bottom_left.y],
        'Rotation': [False]
    }
 
    # Make data frame of above data
    df = pd.DataFrame(data)
    
    # append data frame to CSV file
    df.to_csv('statistic.csv', mode='a', index=False, header=False)

if __name__ == '__main__':

    loadCrate()
    newCrateLength = 1.6
    newCrateWidth = 1

    newCrateX = 15
    newCrateY = 12

    newCrateName = 'randomish'

    newCrate = Rect(Point(newCrateX, newCrateY), Point(newCrateX + newCrateWidth, newCrateY + newCrateLength), newCrateWidth, newCrateLength, newCrateName)
    
    if addCrate(newCrate) :
        updateCSV(newCrate)


    
            


    