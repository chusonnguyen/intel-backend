from ast import Str
import math
from random import randrange
import random
from typing import Dict, List
from unittest import skip
from xmlrpc.client import Boolean, boolean
import numpy as np

from numpy import empty
from sqlalchemy import Integer, true
from .item import Item
from .binmanager import BinManager
import pandas as pd
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

rotate = True
sort = True
pollWidth = 0.0
pollLength = 0.0
pollPosition = 0.0
spaceBetween = 0.0
numOfpol = 0

x_list=[]
y_list=[]
tool_l=[]
tool_w=[]
tool_cr=[]
tool_label = []
tool_rotation = []
zone = []
rowsUnder = []
rowsUpper = []
doubleStackList = []
poll_x = []
poll_y = []
"""
Crate là data class được tạo ra để lưu data extract từ datasheet
Khi data được đọc từ file thì sẽ lưu thành dạng Crate sau đó mới chuyển thành Item để bỏ vào analyze 
vì width và length của Item được tính toán từ width và length của Crate sau khi thêm ailse
"""
class Crate(object):
    def __init__(self, spaces, area, ailse, length, width, height, weights, id: str, double):
        self.spaces = spaces
        self.area = area
        self.ailse = ailse
        self.length = length
        self.width = width
        self.height = height
        self.weights = weights
        self.id = id
        self.double = double
    def __repr__(self):
        return 'Crate(id = %r length=%r, width=%r)' % (self.id, self.length, self.width)
    def set_tracking_number(self, tracking_number):
         self.tracking_number = tracking_number

    def get_tracking_number(self):
         return self.tracking_number


"""
AnalyzingResult là data class dùng để lưu những report sau khi phân tích kết quả của 24 phép sắp xếp khác nhau, các attribute bao gồm:
    1. fit - Boolean: xem algorythm này có sắp xếp được tất cả các Item trong list vào bin ko, nếu có là True, không là False
    2. spaceUsed - float: (Đây không phải honeycombing rate) giá trị này là phần trăm thể hiện sự tối ưu hóa diện tích của algorythm sau khi xếp các Item vào bin, spaceUsed càng cao thì càng hiệu quả
    3. crateUsed - int: số lượng item có thể xếp được vào bin
"""
class AnalyzingResult(object):
    def __init__(self, fit: Boolean, spaceUsed: float, crateUsed: int, honeycomb: float, algo, heuristic, usedList: List):
        self.fit = fit
        self.spaceUsed = spaceUsed
        self.crateUsed = crateUsed
        self.algo = algo
        self.heuristic = heuristic
        self.honeycomb = honeycomb
        self.usedList = usedList
    def __repr__(self) -> str:
        return 'Pack algorythm: %r , heuristic: %r has result: Space maximum= %r, Occupied_Space= %r percentage, Honeycomb = %r percentage, Number of crate fit in bins= %r' % (self.algo, self.heuristic, self.fit, self.spaceUsed, self.honeycomb, self.crateUsed)

def cal_occupied_area(itemList: List) -> float:
    itemList.sort(key = lambda c: c.x+c.width, reverse=True)
    max_x = itemList[0].x + itemList[0].width
    itemList.sort(key = lambda c: c.y+c.height, reverse=True)
    max_y = itemList[0].y + itemList[0].height
    return max_x * max_y

def analyze(bm: BinManager, filled_occupied: float, width: float, height: float):
    space_maximum = True
    occupied_space_percentage = 0.0
    itemList = bm.bins[0].items
    usedCrate = len(itemList)
    occupied_space = cal_occupied_area(itemList)
    honeycombrate = calculateHoneycomb(bm, width, height)
    # see how many outcome does the algorythm produce, if len(bm.bins) > 1 then algo này không thể xếp tất cả Item vào bin
    if len(bm.bins) > 1:
        space_maximum = False
        unfilled_occupied = sum((item.width * item.height) for item in itemList)
        occupied_space_percentage = (unfilled_occupied / occupied_space) * 100
        return AnalyzingResult(space_maximum, occupied_space_percentage, usedCrate, honeycombrate, bm.pack_algo, bm.heuristic, itemList)
    else: 
        occupied_space_percentage = (filled_occupied / occupied_space) * 100
        return AnalyzingResult(space_maximum, occupied_space_percentage, usedCrate, honeycombrate, bm.pack_algo, bm.heuristic, itemList)


# function này chỉ để em visualize trong lúc làm vì cái file matplotlib_demo của em không vẽ được
def drawBins(bm: BinManager, width, height, crateList):

    #define Matplotlib figure and axis
    fig, ax = plt.subplots()

    #create simple line plot
    ax.plot([0, width],[0, height])

    #add rectangle to plot
    itemList = bm.bins[0].items

    topItemList = []
    for topItem in itemList:
        compareList = [item for item in itemList if ((item.y >= (topItem.y + topItem.height)) and (item.x + item.width) >= topItem.x)]
        if len(compareList) == 0 :
            topItemList.append(topItem)
    topItemList.sort(key=lambda c: c.x, reverse=False)
    startinPoint = 0
    for index in range(len(topItemList)):
        if index == len(topItemList) - 1:
            ax.add_patch(Rectangle((topItemList[index].x, topItemList[index].y + topItemList[index].height + 0.05), width - topItemList[index].x , height - (topItemList[index].y + topItemList[index].height) - 0.05 , edgecolor = 'red',facecolor = 'white',fill=True))
        else:
            if ((topItemList[index].y + topItemList[index].height) < (topItemList[index + 1].y + topItemList[index + 1].height)):
                endPoint = topItemList[index + 1].x
            else:
                endPoint = topItemList[index].x + topItemList[index].width
            if index != 0:
                startPoint = startinPoint
            else:
                startPoint = topItemList[index].x
            ax.add_patch(Rectangle((startPoint, topItemList[index].y + topItemList[index].height + 0.05), endPoint - startPoint , height - (topItemList[index].y + topItemList[index].height) - 0.05 , edgecolor = 'red',facecolor = 'white',fill=True))   
            startinPoint = endPoint

    topXItemList = []
    for topXitem in itemList:
        compareXList = [item for item in itemList if ((item.x >= (topXitem.x + topXitem.width)) and (item.y + item.height) >= topXitem.y)]
        if (len(compareXList) == 0) :
            topXItemList.append(topXitem)
    topXItemList.sort(key=lambda c: c.y + c.height, reverse=False)
    for item in topXItemList:
        if ((item not in topItemList) or (item == topItemList[len(topItemList) - 1])):
            ax.add_patch(Rectangle((item.x + item.width + 0.05, item.y), width - (item.x + item.width + 0.05) , item.height , edgecolor = 'red',facecolor = 'white',fill=True))   
    
    
    for item in itemList:
        subLlist = [crate for crate in crateList if str(crate.id) == item.name]
        ax.add_patch(Rectangle((item.x, item.y), item.width , item.height , facecolor = 'pink',fill=True))  
        if (subLlist[0].double == "Yes") :
            if item.y == 0 :
                ax.add_patch(Rectangle((item.x + 0.2, item.y), item.width - 0.8  , item.height - 0.8  ,facecolor = 'yellow',fill=True)) 
            else: 
                ax.add_patch(Rectangle((item.x + 0.2, item.y + 0.2), item.width - 0.8  , item.height - 0.8  ,facecolor = 'yellow',fill=True))
        else :
            ax.add_patch(Rectangle((item.x, item.y), item.width - 0.5 , item.height - 0.5 ,facecolor = 'orange',fill=True))
        if item in topXItemList:
            ax.add_patch(Rectangle((item.x, item.y), item.width - 0.5 , item.height - 0.5 ,facecolor = 'red',fill=True)) 

    plt.savefig('Zone A layout (without poll)', bbox_inches="tight", dpi=150)
    # plt.show()

def checkRotation(item, crate) -> boolean:
    stack = item.width - 0.9
    no_stack = item.width - 0.5
    if (math.isclose(stack, round(crate.width,2)) or math.isclose(no_stack, round(crate.width,2))) :
        return False
    else:
        return True
def getLabel(name: str, crateList: List):
    nameList = name.split("x")
    subLlist = [crate for crate in crateList if crate.get_tracking_number() == nameList[1].strip()]
    return str(subLlist[0].id)
    


def drawBinsWithPoll(first: List, second: List, crateList: List, width, height):

    listDoubleStack = [crate for crate in crateList if crate.double == "Yes"]
    #define Matplotlib figure and axis
    fig, ax = plt.subplots()

    #create simple line plot
    ax.plot([0, width],[0, height], ls='')

    stackColor = '#FEE2C5'
    nonStackColor = '#F3DA0B'
    ailseColor = '#D3D3D3'
    
    # To export statistic.csv
    list_exact_bin = []  
    
    for item in first:
        subLlist = [crate for crate in crateList if str(crate.id) == item.name]
        tool_rotation.append(checkRotation(item, subLlist[0]))
        name = subLlist[0].get_tracking_number()
        ax.add_patch(Rectangle((item.x, item.y), item.width , item.height , facecolor = 'none', edgecolor = ailseColor, hatch='/////', fill=True))  
        doubleStackList.append(subLlist[0].double)
        if (subLlist[0].double == "Yes") :
            topItem = [crate for crate in listDoubleStack if crate.spaces == subLlist[0].spaces]
            if (len(topItem) != 0 and topItem[0].id != subLlist[0].id):
                name = name +" x "+topItem[0].get_tracking_number()
                tool_label.append(item.name+" x "+str(topItem[0].id))
            else:
                tool_label.append(item.name+" x "+getLabel(name, crateList))
            if item.x == 0 and item.y != 0 :
                rect = ax.add_patch(Rectangle((item.x, item.y + 0.45), item.width - 0.45, item.height - 0.9, facecolor=stackColor, lw=0.2, label=item.name)) 
                plt.text(item.x + (item.width/2) - 0.4, item.y + (item.height/2) - 0.25, name, fontsize=4, rotation=90)
                list_exact_bin.append(rect)
            elif item.y == 0 and item.x !=0:
                plt.text(item.x + (item.width/2) - 0.15, item.y + (item.height/2) - 0.5, name, fontsize=4, rotation=90)
                rect = ax.add_patch(Rectangle((item.x + 0.45, item.y), item.width - 0.9, item.height - 0.45, facecolor=stackColor, lw=0.2, label=item.name))
                list_exact_bin.append(rect)
            elif item.y == 0 and item.y == 0:
                rect = ax.add_patch(Rectangle((item.x, item.y), item.width - 0.45, item.height - 0.45, facecolor=stackColor, lw=0.2, label=item.name))
                plt.text(item.x + (item.width/2) - 0.4, item.y + (item.height/2) - 0.2, name, fontsize=4, rotation=90)
                list_exact_bin.append(rect)
            else:
                rect = ax.add_patch(Rectangle((item.x + 0.45, item.y + 0.45), item.width - 0.9, item.height - 0.9, facecolor=stackColor, lw=0.2, label=item.name))
                plt.text(item.x + (item.width/2) - 0.2, item.y + (item.height/2) - 0.25, name, fontsize=4, rotation=90)
                list_exact_bin.append(rect)
        else :
            tool_label.append(item.name)
            if item.x == 0 and item.y != 0:
                rect = ax.add_patch(Rectangle((item.x, item.y + 0.25), item.width - 0.25, item.height - 0.5, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.6, item.y + (item.height/2) - 0.05, name, fontsize=4)
                list_exact_bin.append(rect)
            elif item.y == 0 and item.x !=0:
                rect = ax.add_patch(Rectangle((item.x + 0.25, item.y), item.width - 0.5, item.height  - 0.25, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.3, item.y + (item.height/2) - 0.2, name, fontsize=4)
                list_exact_bin.append(rect)
            elif item.x == 0 and item.y == 0:
                rect = ax.add_patch(Rectangle((item.x, item.y), item.width - 0.25, item.height  - 0.25, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.4, item.y + (item.height/2) - 0.2, name, fontsize=4)    
                list_exact_bin.append(rect)      
            else:
                rect = ax.add_patch(Rectangle((item.x + 0.25, item.y + 0.25), item.width - 0.5, item.height - 0.5, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.3, item.y + (item.height/2) - 0.05, name, fontsize=4)
                list_exact_bin.append(rect)
        tool_cr.append(name)
      
    upperPosition = pollPosition + pollLength - 0.25
    print("Upper position poll postition: " + str(pollPosition))
    print("Upper position: " + str(upperPosition))
    for item in second:
        subLlist = [crate for crate in crateList if str(crate.id) == item.name]
        tool_rotation.append(checkRotation(item, subLlist[0]))
        name = subLlist[0].get_tracking_number()
        ax.add_patch(Rectangle((item.x, item.y + upperPosition), item.width , item.height , facecolor = 'none', edgecolor = ailseColor, hatch='/////',fill=True))  
        doubleStackList.append(subLlist[0].double)
        if (subLlist[0].double == "Yes") :
            topItem = [crate for crate in listDoubleStack if crate.spaces == subLlist[0].spaces]
            if (len(topItem) != 0 and topItem[0].id != subLlist[0].id):
                name = name +" x "+topItem[0].get_tracking_number()
                tool_label.append(item.name+" x "+str(topItem[0].id))
            else:
                tool_label.append(item.name+" x "+getLabel(name, crateList))
            if item.x == 0 :
                rect = ax.add_patch(Rectangle((item.x, item.y + 0.45 + upperPosition), item.width - 0.45, item.height - 0.9, facecolor=stackColor, lw=0.2, label=item.name)) 
                plt.text(item.x + (item.width/2) - 0.4, item.y + (item.height/2) - 0.25 + 6.5, name, fontsize=4, rotation=90)
                list_exact_bin.append(rect)
            # elif item.y == 0 and item.x !=0:
            #     plt.text(item.x + (item.width/2) - 0.15, item.y + (item.height/2) - 0.5 + 6.5, name, fontsize=4, rotation=90)
            #     rect = ax.add_patch(Rectangle((item.x + 0.45, item.y + 6.5), item.width - 0.9, item.height - 0.45 , facecolor=stackColor, lw=0.2, label=item.name))
            #     list_exact_bin.append(rect)
            # elif item.y == 0 and item.y == 0:
            #     rect = ax.add_patch(Rectangle((item.x, item.y + 6.5), item.width - 0.45, item.height - 0.45, facecolor=stackColor, lw=0.2, label=item.name))
            #     plt.text(item.x + (item.width/2) - 0.4, item.y + (item.height/2) - 0.2 + 6.5, name, fontsize=4, rotation=90)
            #     list_exact_bin.append(rect)
            else:
                rect = ax.add_patch(Rectangle((item.x + 0.45, item.y + 0.45 + upperPosition), item.width - 0.9, item.height - 0.9, facecolor=stackColor, lw=0.2, label=item.name))
                plt.text(item.x + (item.width/2) - 0.2, item.y + (item.height/2) - 0.25 + 6.5, name, fontsize=4, rotation=90)
                list_exact_bin.append(rect)
        else :
            tool_label.append(item.name)
            if item.x == 0 :
                rect = ax.add_patch(Rectangle((item.x, item.y + 0.25 + upperPosition), item.width - 0.25, item.height - 0.5, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.6, item.y + (item.height/2) - 0.05 + 6.5, name, fontsize=4)
                list_exact_bin.append(rect)
            # elif item.y == 0 and item.x !=0:
            #     rect = ax.add_patch(Rectangle((item.x + 0.25, item.y + 6.5), item.width - 0.5, item.height  - 0.25, facecolor=nonStackColor, label=item.name))
            #     plt.text(item.x + (item.width/2) - 0.3, item.y + (item.height/2) - 0.2 + 6.5, name, fontsize=4)
            #     list_exact_bin.append(rect)
            # elif item.x == 0 and item.y == 0:
            #     rect = ax.add_patch(Rectangle((item.x, item.y + 6.5), item.width - 0.25, item.height  - 0.25, facecolor=nonStackColor, label=item.name))
            #     plt.text(item.x + (item.width/2) - 0.4, item.y + (item.height/2) - 0.2 + 6.5, name, fontsize=4)          
            #     list_exact_bin.append(rect)
            else:
                rect = ax.add_patch(Rectangle((item.x + 0.25, item.y + 0.25 + upperPosition), item.width - 0.5, item.height - 0.5, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.3, item.y + (item.height/2) - 0.05 + 6.5, name, fontsize=4)
                list_exact_bin.append(rect)
        tool_cr.append(name)
    
    # On the purpose to export statistic.csv
    for item in list_exact_bin:
        x_list.append(round(item.xy[0], 2))
        y_list.append(round(item.xy[1],2))
        tool_l.append(round(item._width, 2))
        tool_w.append(round(item._height, 2))
        zone.append('ZONE B')
    
    
    pollX = 0
    pollY = pollPosition
    for x in range(numOfpol):
        poll_x.append(pollX)
        poll_y.append(pollY)
        ax.add_patch(Rectangle((pollX, pollY ), pollWidth , pollLength, facecolor='none', hatch='\\\\', edgecolor='blue'))
        pollX += spaceBetween + pollWidth

    plt.savefig('Zone A layout', bbox_inches="tight", dpi=150)
    #plt.show()

def calculateHoneycomb(bm: BinManager, width, height) -> float:

    #add rectangle to plot
    itemList = bm.bins[0].items

    topItemList = []
    for topItem in itemList:
        compareList = [item for item in itemList if ((item.y >= (topItem.y + topItem.height)) and (item.x + item.width) >= topItem.x)]
        if len(compareList) == 0 :
            topItemList.append(topItem)
    topItemList.sort(key=lambda c: c.x, reverse=False)
    startinPoint = 0
    freeRecArea = 0.0
    for index in range(len(topItemList)):
        if index == len(topItemList) - 1:
            freeRecArea += (width - topItemList[index].x ) *  (height - (topItemList[index].y + topItemList[index].height))
        else:
            if ((topItemList[index].y + topItemList[index].height) < (topItemList[index + 1].y + topItemList[index + 1].height)):
                endPoint = topItemList[index + 1].x
            else:
                endPoint = topItemList[index].x + topItemList[index].width
            if index != 0:
                startPoint = startinPoint
            else:
                startPoint = topItemList[index].x
            freeRecArea += (endPoint - startPoint) * (height - (topItemList[index].y + topItemList[index].height))
            startinPoint = endPoint

    topXItemList = []
    for topXitem in itemList:
        compareXList = [item for item in itemList if ((item.x >= (topXitem.x + topXitem.width)) and (item.y + item.height) >= topXitem.y)]
        if (len(compareXList) == 0) :
            topXItemList.append(topXitem)
    topXItemList.sort(key=lambda c: c.y + c.height, reverse=False)
    for item in topXItemList:
        if ((item not in topItemList) or (item == topItemList[len(topItemList) - 1])):
            freeRecArea += (width - (item.x + item.width + 0.05)) * (item.height)   
    
    for item in itemList:
        freeRecArea += item.width * item.height

    return (1 - (freeRecArea / (width * height))) * 100
         

def sorting(width: int, height: int, packAlogorythm: Str, heuristic: Str, itemList: list, occupied):
    M = BinManager(width, height, pack_algo=packAlogorythm, heuristic=heuristic, rotation=rotate, sorting=sort, wastemap=True)
    M.add_items(*itemList)
    M.execute()
    return analyze(M, occupied, width, height)

#function dùng để in kết quả, hay thêm render_bin(M, save=True) nếu chạy được, nhớ copy code từ file matplotlib_demo qua 
# Hiện em chưa tính được honeycomb nên nếu ai tính được thì dùng cái M.bins này tính vì đây là kết quả tối ưu nhất
def printResult(result: AnalyzingResult, width, height, itemList, crateList):
    M = BinManager(width, height, pack_algo=result.algo, heuristic=result.heuristic, rotation=rotate, sorting=sort, wastemap=True)
    #M = BinManager(width, height, pack_algo="maximal_rectangle", heuristic="contact_point", rotation=rotate, sorting=sort, wastemap=True)
    M.add_items(*itemList)
    M.execute()
    print(M.bins)
    drawBins(M, width, height, crateList)

def secondRoundAnalyze(remainItemList: List, width, length, crate_instances):
    pack_algo_list = ['skyline','maximal_rectangle','guillotine','shelf']
    heuristicList = ['bottom_left', 'best_fit', 'best_area', 'best_shortside', 'best_longside', 'worst_area', 'worst_shortside', 'worst_longside', 'contact_point','best_width_fit','best_height_fit','best_area_fit','worst_width_fit','worst_height_fit','worst_area_fit','next_fit','first_fit']
    listResult = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for algo in pack_algo_list:
            bin_results = [executor.submit(sorting, width, length , algo, heuris, remainItemList, sum(crateItem.area for crateItem in crate_instances)) for heuris in heuristicList]
            for result in concurrent.futures.as_completed(bin_results):
                try:
                    listResult.append(result.result())
                except Exception as exc:
                    skip
    print('First round analyze (for second part): ')
    for result in listResult :
        print(result)
    listReturn = []
    useAllCrateList = [result for result in listResult if result.fit == True]
    if (len(useAllCrateList) != 0):
        if (len(useAllCrateList) == 1):
            bestResult = useAllCrateList[0]
            rowsUpper.append(['ZONE B', 'Upper', bestResult.algo, bestResult.heuristic, 0, 0, 0, 0])
            listReturn = bestResult.usedList
        else:
            useAllCrateList.sort(key= lambda c: c.honeycomb, reverse=False)
            maxResult = useAllCrateList[0].honeycomb
            bestResult = useAllCrateList[0]
            print('Second round analyze: ')
            print(bestResult)
            global rows
            rowsUpper.append(['ZONE B', 'Upper', bestResult.algo, bestResult.heuristic, 0, 0, 0, 0])
            #printResult(bestResult, width, length, remainItemList, crate_instances)
            listReturn = bestResult.usedList
    else:
        rowsUpper.append(['ZONE B', 'Upper', '', '', 0, 0, 0, 0])
    return listReturn

def calculateHoneycombWithPoll(first: list, second: list, width: float, height: float, crateList: list) ->  float:

    usedArea = 0.0

    # topUnderItemList = []
    # for topUnderItem in first:
    #     compareList = [item for item in first if ((item.y >= (topUnderItem.y + topUnderItem.height)) and (item.x + item.width) >= topUnderItem.x)]
    #     if len(compareList) == 0 :
    #         topUnderItemList.append(topUnderItem)
    # topUnderItemList.sort(key= lambda c: c.y + c.height, reverse=False)
    # if (pollLength + pollPosition - 0.25 - topUnderItemList[0].y - topUnderItemList[0].height) > 1:
    #     usedUnderArea = (pollLength + pollPosition - 0.25) * width - sum(item.width * item.height for item in first)
    #     usedArea += usedUnderArea
    

    total = first[:]
    for item in second:
        total.append(Item(width=item.width, height=item.height, CornerPoint=[item.x, item.y+pollLength+pollPosition], name=item.name))

    topItemList = []
    for topItem in total:
        compareList = [item for item in total if ((item.y >= (topItem.y + topItem.height)) and (item.x + item.width) >= topItem.x)]
        if len(compareList) == 0 :
            topItemList.append(topItem)
    topItemList.sort(key=lambda c: c.x, reverse=False)
    startinPoint = 0
    for index in range(len(topItemList)):
        if index == len(topItemList) - 1:
            usedArea += (width - topItemList[index-1].x - topItemList[index-1].width) * (height - (topItemList[index].y + topItemList[index].height))
        else:
            if ((topItemList[index].y + topItemList[index].height) < (topItemList[index + 1].y + topItemList[index + 1].height)):
                endPoint = topItemList[index + 1].x
            else:
                endPoint = topItemList[index].x + topItemList[index].width
            if index != 0:
                startPoint = startinPoint
            else:
                startPoint = topItemList[index].x
            usedArea += (endPoint - startPoint) * (height - (topItemList[index].y + topItemList[index].height))
            startinPoint = endPoint

    topXItemList = []
    for topXitem in total:
        compareXList = [item for item in total if ((item.x >= (topXitem.x + topXitem.width)) and (item.y + item.height) >= topXitem.y)]
        if (len(compareXList) == 0) :
            topXItemList.append(topXitem)
    topXItemList.sort(key=lambda c: c.y + c.height, reverse=False)
    for item in topXItemList:
        if ((item not in topItemList) or (item == topItemList[len(topItemList) - 1])):
            usedArea += (width - (item.x + item.width + 0.05)) * (item.height)

    for item in total:
        usedArea += item.width * item.height


    honeycomb = ((width * height) - usedArea) / (width * height)
    honey = round(honeycomb * 100, 2)
    if (honey <= 0):
        return honey * -1
    else :
        return honey

def main(df, w, l ,totalPoll, pollRow, pollW, pollL, pollX, pollY, pollGap ,pollRowGap):
    print(type(w))
    print(type(l))
    poll = True
    binWidth = float(w)  #độ rộng của bin (zone), chỉnh sửa ở đây nếu cần thay đổi kích thước
    binMaxLength = float(l)  #độ dài của bin (zone), chỉnh sửa ở đây nếu cần thay đổi kích 
    global pollWidth
    pollWidth = float(pollW)
    global pollLength
    pollLength = float(pollL)
    global pollPosition
    pollPosition = float(pollY)
    print("pollPosition: "+ str(pollPosition))
    print("poll Y"+ str(pollY))
    global spaceBetween
    spaceBetween = float(pollGap)
    global numOfpol
    numOfpol = int(totalPoll)
    if poll == True:
        binLength = pollPosition + 0.25
    else :
        binLength = binMaxLength
    poll_x.clear()
    poll_y.clear()
    
    """
    Cái block code get data from file là em dùng để đọc dữ liệu từ cái file 
    """
    # Get data from file
    #df = pd.read_excel('Full tool list.xlsx')
    df = df[df['Occupied space'].notna()]
    colList = ["Occupied space", "Tool sqm", "Ailse", "Length", "Width", "Height", "Weights", "Crate Label", "Double stack"]
    dataColName = df.columns.tolist()
    indexList = []
    for colName in colList:
        indexList.append(dataColName.index(colName))
    crateInfoList = df.values.tolist()

    crate_instances = [] # Danh sách các Crate sau khi đọc xong
    for crateInfo in crateInfoList:
        crate_instances.append(Crate(*[crateInfo[index] for index in indexList]))

    tracking_number = 1
    for crate in crate_instances:
        crate.set_tracking_number(str(tracking_number))
        tracking_number += 1
    
    
    doubleStackFull = [crate for crate in crate_instances if crate.double == "Yes"]
    doubleStackSpaceEqualOnTop = []
    spaceEqual = []
    for index in range(len(doubleStackFull)):
        equal = doubleStackFull[index].spaces
        for index2 in range(len(doubleStackFull)):
            if index2 == index:
                continue
            else :
                if (doubleStackFull[index2].spaces == equal):
                    if doubleStackFull[index2].spaces in spaceEqual:
                        doubleStackSpaceEqualOnTop.append(doubleStackFull[index2])
                        continue
                    else:
                        spaceEqual.append(doubleStackFull[index2].spaces)
    doubleStackSpaceNotEquall = [crate for crate in doubleStackFull if crate.spaces not in spaceEqual]
    doubleStackSpaceNotEquall.sort(key=lambda c:c.spaces, reverse=False)
    doubleStackSpaceNotEquallOntop = []
    subIndex = 0
    while subIndex < len(doubleStackSpaceNotEquall):
        doubleStackSpaceNotEquallOntop.append(doubleStackSpaceNotEquall[subIndex])
        for crate in crate_instances:
            if crate.id == doubleStackSpaceNotEquall[subIndex + 1].id :
                crate.set_tracking_number(crate.get_tracking_number() + " x " + doubleStackSpaceNotEquall[subIndex].get_tracking_number())
        if ((subIndex + 1) == len(doubleStackSpaceNotEquall)) :
            doubleStackSpaceNotEquallOntop.append(doubleStackSpaceNotEquall[subIndex + 1])
        subIndex += 2
    removeList = doubleStackSpaceEqualOnTop + doubleStackSpaceNotEquallOntop
    crate_instances_use = [crate for crate in crate_instances if crate not in removeList]
    print(len(crate_instances_use))

    """
    Khúc này là để bỏ từ Crate list vào Item list, hiện chỉ dùng đúng width và length chứ ko có ailse, sẽ thêm sau nếu cần
    sau này sau khi đã có xong algorythm để Stack thì thêm vào sau cái này để xử lý cái list maximal 
    """
    maximal = [] 
    for crate in crate_instances_use:
        if (crate.double == "Yes") :
            maximal.append(Item(round(crate.width, 2) + 0.9, round(crate.length, 2) + 0.9, str(crate.id)))
        else :
            maximal.append(Item(round(crate.width, 2) + 0.5, round(crate.length, 2) + 0.5, str(crate.id)))
   

    #Lấy ra Item có size bé nhất để dùng cho cái function maximumFreeRectangle ở trên
    maximal.sort(key= lambda c: c.width*c.height)
    smallestItem = maximal[0]

    # Dùng processpool để tăng tốc độ
    pack_algo_list = ['skyline','maximal_rectangle','guillotine','shelf']
    heuristicList = ['bottom_left', 'best_fit', 'best_area', 'best_shortside', 'best_longside', 'worst_area', 'worst_shortside', 'worst_longside', 'contact_point','best_width_fit','best_height_fit','best_area_fit','worst_width_fit','worst_height_fit','worst_area_fit','next_fit','first_fit']
    listResult = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for algo in pack_algo_list:
            bin_results = [executor.submit(sorting, binWidth, binLength , algo, heuris, maximal, sum(crateItem.area for crateItem in crate_instances_use)) for heuris in heuristicList]
            for result in concurrent.futures.as_completed(bin_results):
                try:
                    listResult.append(result.result())
                except Exception as exc:
                    skip
    
    print('First round analyze: ')
    for result in listResult :
        print(result) # in kết quả sau khi chạy (đã tính toán spaceUsed và crateUsed)

    """
    Nguyên khúc dưới đây là để phân tích dữ liệu sau khi chạy, cơ bản là chọn algo xếp được nhiều bins nhất và lượng space dùng optimize nhất
    """    
    honeycombRate = 0.0
    useAllCrateList = [result for result in listResult if result.fit == True]
    unuseAllCrateList = [result for result in listResult if result.fit == False]
    if (len(useAllCrateList) != 0):
        if (len(useAllCrateList) == 1):
            bestResult = useAllCrateList[0]
            printResult(bestResult, binWidth, binLength, maximal, crate_instances)
            rowsUnder.append(['ZONE B', 'Under', bestResult.algo, bestResult.heuristic, 0, 0, 0, 0])
        else:
            useAllCrateList.sort(key= lambda c: c.honeycomb, reverse=False)
            maxResult = useAllCrateList[0].honeycomb
            resultCount = sum(map(lambda x: x.honeycomb == maxResult, useAllCrateList))
            bestResult = useAllCrateList[0]
            print(bestResult)
            printResult(bestResult, binWidth, binLength, maximal, crate_instances)
            rowsUnder.append(['ZONE B', 'Under', bestResult.algo, bestResult.heuristic, 0, 0, 0, 0])          
    else:
        unuseAllCrateList.sort(key= lambda c: c.spaceUsed, reverse=True)
        maxResult = unuseAllCrateList[0].spaceUsed
        resultCount = sum(map(lambda x: x.spaceUsed == maxResult, unuseAllCrateList))
        if resultCount == 1:
            bestResult = unuseAllCrateList[0]
            print('Second round analyze: ')
            print(bestResult)
            rowsUnder.append(['ZONE B', 'Under', bestResult.algo, bestResult.heuristic, 0, 0, 0, 0])
            if poll == True:
                firstRoundList = bestResult.usedList
                part1 = [item.name for item in bestResult.usedList]
                part2 = [item for item in maximal if item.name not in part1]
                crate_instances_second = [crateItem for crateItem in crate_instances_use if str(crateItem.id) not in part1]
                secondRoundlist = secondRoundAnalyze(part2, binWidth, binMaxLength - binLength, crate_instances_second)
                if (len(secondRoundlist) != 0):
                    honeycombRate = calculateHoneycombWithPoll(firstRoundList, secondRoundlist, binWidth, binMaxLength, crate_instances_use)
                else:
                    honeycombRate = 0
                drawBinsWithPoll(firstRoundList, secondRoundlist, crate_instances, binWidth, binMaxLength)
            else :
                printResult(bestResult, binWidth, binLength, maximal, crate_instances_use)
        else:
            sameSpaceUsedList = [result for result in unuseAllCrateList if result.spaceUsed == maxResult]
            print('Second round analyze: ')
            for result in sameSpaceUsedList :
                print(result)
            bestResult = sameSpaceUsedList[0]
            rowsUnder.append(['ZONE B', 'Under', bestResult.algo, bestResult.heuristic, 0, 0, 0, 0])
            if poll == True:
                firstRoundList = bestResult.usedList
                part1 = [item.name for item in bestResult.usedList]
                part2 = [item for item in maximal if item.name not in part1]
                crate_instances_second = [crateItem for crateItem in crate_instances_use if str(crateItem.id) not in part1]
                secondRoundlist = secondRoundAnalyze(part2, binWidth, binMaxLength - binLength, crate_instances_second)
                honeycombRate = calculateHoneycombWithPoll(firstRoundList, secondRoundlist, binWidth, binMaxLength, crate_instances_use)
                drawBinsWithPoll(firstRoundList, secondRoundlist, crate_instances, binWidth, binMaxLength)
            else :
                printResult(bestResult, binWidth, binLength, maximal, crate_instances_use)

                
    # Export statistic.csv
    #x_list = [ '%.2f' % elem for elem in x_list ]
    #y_list = [ '%.2f' % elem for elem in y_list ]
      
    dict = {'Crate':tool_cr[(len(tool_cr) - len(crate_instances_use)):len(tool_cr)],'Label':tool_label[(len(tool_cr) - len(crate_instances_use)):len(tool_label)], 'width': tool_w[(len(tool_cr) - len(crate_instances_use)):len(tool_w)], 'Length': tool_l[(len(tool_cr) - len(crate_instances_use)):len(tool_l)], 'x':x_list[(len(tool_cr) - len(crate_instances_use)):len(tool_cr)], 'y':y_list[(len(tool_cr) - len(crate_instances_use)):len(tool_cr)], 'Rotation': tool_rotation[(len(tool_cr) - len(crate_instances_use)):len(tool_cr)], 'Zone':zone[(len(tool_cr) - len(crate_instances_use)):len(tool_cr)], 'Double Stack':doubleStackList[(len(tool_cr) - len(crate_instances_use)):len(tool_cr)]}
    df_statistic = pd.DataFrame(dict)
    df_statistic.to_csv('statistic.csv')
    print(len(crate_instances_use))
    usableSpace = (float(l) * float(w)) - (float(l) * float(w))*float(honeycombRate) / 100 - sum(crateItem.area for crateItem in crate_instances_use)
    rowsUpper[0][4] = honeycombRate
    rowsUnder[0][4] = honeycombRate
    rowsUpper[0][5] = usableSpace
    rowsUnder[0][5] = usableSpace
    rowsUpper[0][6] = len(crate_instances)
    rowsUnder[0][6] = len(crate_instances)
    rowsUpper[0][7] = len(doubleStackFull)
    rowsUnder[0][7] = len(doubleStackFull)
    rows = rowsUnder[0:1] + rowsUpper[0:1]
    np.savetxt("algo.csv", 
           rows,
           delimiter =", ", 
           fmt ='% s')
    dict_poll = {'PollX':poll_x, 'PollY':poll_y}
    df_poll = pd.DataFrame(dict_poll)
    df_poll.to_csv('poll.csv')
   
                

