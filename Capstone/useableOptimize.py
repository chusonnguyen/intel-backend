from tkinter.tix import Tree
from procespool import *
from updatelayout import *
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

def sortUpper() -> list:
    df_statistic = pd.read_csv("statistic.csv")
    trackingNumber = df_statistic['Crate'].tolist()
    Xaxis = df_statistic['X-axis'].tolist()
    Yaxis = df_statistic['Y-axis'].tolist()
    rotation = df_statistic['Rotation'].tolist()

    itemList = []

    for index in range(len(trackingNumber)):
        getCrate = [crate for crate in crate_instances if crate.get_tracking_number() == trackingNumber[index]]
        if len(getCrate) > 0:
            if getCrate[0].double == "Yes":
                itemList.append(Item(width=getCrate[0].width + 0.9, height=getCrate[0].length + 0.9, name=getCrate[0].get_tracking_number(), CornerPoint=[Xaxis[index], Yaxis[index]]))
            else:
                itemList.append(Item(width=getCrate[0].width + 0.5, height=getCrate[0].length + 0.5, name=getCrate[0].get_tracking_number(), CornerPoint=[Xaxis[index], Yaxis[index]]))

        else:
            exatTrankingNumber = trackingNumber[index].split(" x ")
            getStackCrate = [crate for crate in crate_instances if crate.get_tracking_number() == exatTrankingNumber[0]]
            if getStackCrate[0].double == "Yes":
                itemList.append(Item(width=getStackCrate[0].width + 0.9, height=getStackCrate[0].length + 0.9, name=getStackCrate[0].get_tracking_number(), CornerPoint=[Xaxis[index], Yaxis[index]]))
            else:
                itemList.append(Item(width=getStackCrate[0].width + 0.5, height=getStackCrate[0].length + 0.5, name=getStackCrate[0].get_tracking_number(), CornerPoint=[Xaxis[index], Yaxis[index]]))
    itemListSort = [item for item in itemList if item.y >= pollLength + pollPosition - 0.25]
    newList = sorted(itemListSort, key = lambda x: (x.y, x.x))

    return newList

    


if __name__ == '__main__':

    loadCrate()
    #sortUnder()
    listRetrun = sortUpper()
    M = BinManager(binWidth, binLength - pollLength - pollPosition + 0.25, pack_algo='maximal_rectangle', heuristic='contact_point', rotation=True, sorting=False)
    M.add_items(*listRetrun)
    M.execute()
    print(listRetrun)
    print(M.bins)
    #sortFull()