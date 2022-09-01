from ast import Str
import math
from random import randrange
import random
from typing import Dict, List
from unittest import skip
from xmlrpc.client import Boolean, boolean
import numpy as np

from numpy import empty
from sqlalchemy import Integer, false, true
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
pollWidth = 0.2
pollLength = 0.5
pollPosition = 6
spaceBetween = 5.6
numOfpol = 7
pollRowGap = 0
indicator = 0
wsaaLoop = 0
binWidth = 0 #độ rộng của bin (zone), chỉnh sửa ở đây nếu cần thay đổi kích thước
binMaxLength = 0  #độ dài của bin (zone), chỉnh sửa ở đây nếu cần thay đổi kích 

x_list=[]
y_list=[]
tool_l=[]
tool_w=[]
tool_cr=[]
tool_label = []
tool_rotation = []
zone = []
rowsUpper = []
doubleStackList = []
cordinateList = []
numOfCrate = []
globalItemList = []
poll_x = []
poll_y = []
ailse_x = []
ailse_y = []
ailse_w = []
ailse_l = []

"""
Crate là data class được tạo ra để lưu data extract từ datasheet
Khi data được đọc từ file thì sẽ lưu thành dạng Crate sau đó mới chuyển thành Item để bỏ vào analyze 
vì width và length của Item được tính toán từ width và length của Crate sau khi thêm ailse
"""
class CrateRow(object):
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
        return 'CrateRow(id = %r length=%r, width=%r)' % (self.id, self.length, self.width)
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
         

def sorting(width: int, height: int, packAlogorythm: Str, heuristic: Str, itemList: list, occupied, sorting):
    M = BinManager(width, height, pack_algo=packAlogorythm, heuristic=heuristic, rotation=rotate, sorting=sort, wastemap=True, sorting_heuristic=sorting)
    M.add_items(*itemList)
    M.execute()
    return analyze(M, occupied, width, height)

def drawBinsWithMultipleRows(first: List, crateList: List, width, height):

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
    itemNum = 1
    position = 0
    for item in first:
        for index in range(len(numOfCrate)):
            itemCount = sum(i for i in numOfCrate[0:index+1])
            if index == 0 and itemNum <= itemCount :
                position = 0
                break
            elif itemNum <= itemCount:
                position = pollPosition + pollLength + (index-1) * (pollRowGap + pollLength)
                break
        itemNum += 1
        subLlist = [crate for crate in crateList if str(crate.id) == item.name]
        tool_rotation.append(checkRotation(item, subLlist[0]))
        name = subLlist[0].get_tracking_number()
        ax.add_patch(Rectangle((item.x, item.y + position), item.width , item.height , facecolor = 'none', edgecolor = ailseColor, hatch='/////', fill=True))  
        ailse_x.append(item.x)
        ailse_y.append(item.y + position)
        ailse_w.append(item.width)
        ailse_l.append(item.height)
        doubleStackList.append(subLlist[0].double)
        if (subLlist[0].double == "Yes") :
            topItem = [crate for crate in listDoubleStack if crate.spaces == subLlist[0].spaces]
            if (len(topItem) != 0 and topItem[0].id != subLlist[0].id):
                name = name +" x "+topItem[0].get_tracking_number()
                tool_label.append(item.name+" x "+str(topItem[0].id))
            else:
                if "x" in name:
                    tool_label.append(item.name+" x "+getLabel(name, crateList))
                else:
                    tool_label.append(item.name)
            if item.x == 0 and item.y != 0 :
                rect = ax.add_patch(Rectangle((item.x, item.y + 0.45 + position), item.width - 0.45, item.height - 0.9, facecolor=stackColor, lw=0.2, label=item.name)) 
                plt.text(item.x + (item.width/2) - 0.4, item.y + (item.height/2) - 0.25 + position, name, fontsize=4, rotation=90)
                list_exact_bin.append(rect)
            elif item.y == 0 and item.x !=0:
                plt.text(item.x + (item.width/2) - 0.15, item.y + (item.height/2) - 0.5 + position, name, fontsize=4, rotation=90)
                rect = ax.add_patch(Rectangle((item.x + 0.45, item.y + position), item.width - 0.9, item.height - 0.45, facecolor=stackColor, lw=0.2, label=item.name))
                list_exact_bin.append(rect)
            elif item.y == 0 and item.y == 0:
                rect = ax.add_patch(Rectangle((item.x, item.y + position), item.width - 0.45, item.height - 0.45, facecolor=stackColor, lw=0.2, label=item.name))
                plt.text(item.x + (item.width/2) - 0.4, item.y + (item.height/2) - 0.2 + position, name, fontsize=4, rotation=90)
                list_exact_bin.append(rect)
            else:
                rect = ax.add_patch(Rectangle((item.x + 0.45, item.y + 0.45 + position), item.width - 0.9, item.height - 0.9, facecolor=stackColor, lw=0.2, label=item.name))
                plt.text(item.x + (item.width/2) - 0.2, item.y + (item.height/2) - 0.25 + position, name, fontsize=4, rotation=90)
                list_exact_bin.append(rect)
        else :
            tool_label.append(item.name)
            if item.x == 0 and item.y != 0:
                rect = ax.add_patch(Rectangle((item.x, item.y + 0.25 + position), item.width - 0.25, item.height - 0.5, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.6, item.y + (item.height/2) - 0.05 + position, name, fontsize=4)
                list_exact_bin.append(rect)
            elif item.y == 0 and item.x !=0:
                rect = ax.add_patch(Rectangle((item.x + 0.25, item.y + position), item.width - 0.5, item.height  - 0.25, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.3, item.y + (item.height/2) - 0.2 + position, name, fontsize=4)
                list_exact_bin.append(rect)
            elif item.x == 0 and item.y == 0:
                rect = ax.add_patch(Rectangle((item.x, item.y + position), item.width - 0.25, item.height  - 0.25, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.4, item.y + (item.height/2) - 0.2 + position, name, fontsize=4)    
                list_exact_bin.append(rect)      
            else:
                rect = ax.add_patch(Rectangle((item.x + 0.25, item.y + 0.25 + position), item.width - 0.5, item.height - 0.5, facecolor=nonStackColor, label=item.name))
                plt.text(item.x + (item.width/2) - 0.3, item.y + (item.height/2) - 0.05 + position, name, fontsize=4)
                list_exact_bin.append(rect)
        tool_cr.append(name)
    
    # On the purpose to export statistic.csv
    for item in list_exact_bin:
        x_list.append(round(item.xy[0], 2))
        y_list.append(round(item.xy[1],2))
        tool_l.append(round(item._width, 2))
        tool_w.append(round(item._height, 2))
        zone.append('ZONE B')

    
    
    for count in range(wsaaLoop):
        pollX = 0
        pollY = pollPosition + count * (pollRowGap + pollLength)
        for x in range(numOfpol):
            poll_x.append(pollX)
            poll_y.append(pollY)
            ax.add_patch(Rectangle((pollX, pollY ), pollWidth , pollLength, facecolor='none', hatch='\\\\', edgecolor='blue'))
            pollX += spaceBetween + pollWidth



    plt.savefig('Row layout (row)', bbox_inches="tight", dpi=150)
    #plt.show()

def algorythmExecute(remainItemList: List, width, length, crate_instances_use, crate_instances):
  global indicator, cordinateList, numOfCrate
  if (indicator <= wsaaLoop or (wsaaLoop == 0 and indicator == 0)) :
    pack_algo_list = ['maximal_rectangle']
    heuristicList = ['bottom_left', 'best_area', 'best_shortside', 'best_longside', 'worst_area', 'worst_shortside', 'worst_longside', 'contact_point']
    listResult = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for algo in pack_algo_list:
            bin_results = [executor.submit(sorting, width, length , algo, heuris, remainItemList, sum(crateItem.area for crateItem in crate_instances_use), 'DESCA') for heuris in heuristicList]
            for result in concurrent.futures.as_completed(bin_results):
                try:
                    listResult.append(result.result())
                except Exception as exc:
                    print('Error here')
                    skip
    print(str(indicator) + ' round analyze (row): ')
    for result in listResult :
        print(result)
    useAllCrateList = [result for result in listResult if result.fit == True]
    unuseAllCrateList = [result for result in listResult if result.fit == False]
    if wsaaLoop != 0:
        useAllCrateList.sort(key= lambda c: (c.spaceUsed,c.honeycomb), reverse=True)
        unuseAllCrateList.sort(key= lambda c: (c.spaceUsed,c.honeycomb), reverse=True)
    else:
        useAllCrateList.sort(key= lambda c: c.crateUsed, reverse=True)
        unuseAllCrateList.sort(key= lambda c: c.crateUsed, reverse=True)
    if (len(useAllCrateList) != 0 ):
        bestResult = useAllCrateList[0]
    elif (len(unuseAllCrateList) != 0 ) :
        bestResult = unuseAllCrateList[0]
    else:
        bestResult = AnalyzingResult(false, 0, 0, 0, '', '', listResult)
    cordinateList.extend(bestResult.usedList)
    numOfCrate.append(bestResult.crateUsed)
    nameList = [item.name for item in cordinateList]
    remainList = [item for item in globalItemList if item.name not in nameList]
    print(len(remainList))
    if (len(remainList) != 0):
        indicator = indicator + 1
        rowsUpper.append(['ZONE B', 'Upper', bestResult.algo, bestResult.heuristic, 0, 0, 0, 0])
        algorythmExecute(remainList, width, pollRowGap+pollLength-0.25, crate_instances_use, crate_instances)

    else:
        rowsUpper.append(['ZONE B', 'Upper', bestResult.algo, bestResult.heuristic, 0, 0, 0, 0])
        indicator = wsaaLoop
def calculateHoneycombWithMultiplePoll(corList: List, width: float, height: float, crateList: list) ->  float:

    usedArea = 0.0
    total = []
    itemNum = 1
    position = 0
    for item in corList:
        for index in range(len(numOfCrate)):
            itemCount = sum(i for i in numOfCrate[0:index+1])
            if index == 0 and itemNum <= itemCount :
                position = 0
                break
            elif itemNum <= itemCount:
                position = pollPosition + pollLength + (index-1) * (pollRowGap + pollLength)
                break
        total.append(Item(width=item.width, height=item.height, CornerPoint=[item.x, item.y+position], name=item.name))
        itemNum += 1

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


    honeycomb = ((width * height) - usedArea) * 100 / (width * height)
    if honeycomb < 0:
        return round(honeycomb, 2) * -1 
    return round(honeycomb, 2)

def mainRow(df, w, l ,totalPoll, pollRow, pollW, pollL, pollX, pollY, pollGap, pollRGap):
    print(type(w))
    print(type(l))
    global binWidth, binMaxLength, pollWidth, pollLength, pollPosition, spaceBetween, numOfpol, pollRowGap
    binWidth = float(w)  #độ rộng của bin (zone), chỉnh sửa ở đây nếu cần thay đổi kích thước
    binMaxLength = float(l)  #độ dài của bin (zone), chỉnh sửa ở đây nếu cần thay đổi kích 
    pollWidth = float(pollW)
    pollLength = float(pollL)
    pollPosition = float(pollY)
    spaceBetween = float(pollGap)
    numOfpol = int(totalPoll)
    pollRowGap = int(pollRGap)
    numOfCrate.clear()
    cordinateList.clear()
    tool_cr.clear()
    tool_l.clear()
    tool_label.clear()
    tool_rotation.clear()
    tool_w.clear()
    x_list.clear()
    y_list.clear()
    zone.clear()
    doubleStackList.clear()
    globalItemList.clear()
    poll_x.clear()
    poll_y.clear()
    ailse_x.clear()
    ailse_y.clear()
    ailse_w.clear()
    ailse_l.clear()
    """
    Cái block code get data from file là em dùng để đọc dữ liệu từ cái file 
    """
    # Get data from file
    df = df[df['Occupied space'].notna()]
    colList = ["Occupied space", "Tool sqm", "Ailse", "Length", "Width", "Height", "Weights", "Crate Label", "Double stack"]
    dataColName = df.columns.tolist()
    indexList = []
    for colName in colList:
        indexList.append(dataColName.index(colName))
    crateInfoList = df.values.tolist()

    crate_instances = [] # Danh sách các CrateRow sau khi đọc xong
    for crateInfo in crateInfoList:
        crate_instances.append(CrateRow(*[crateInfo[index] for index in indexList]))

    tracking_number = 1
    for crate in crate_instances:
        crate.set_tracking_number(str(tracking_number))
        tracking_number += 1
    
    
    doubleStackFull = [crate for crate in crate_instances if crate.double == "Yes"]
    doubleStackSpaceEqualOnTop = []
    spaceEqual = []
    if len(doubleStackFull) > 1:
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
            if ((subIndex + 1) >= len(doubleStackSpaceNotEquall)) :
                break
            else:
                doubleStackSpaceNotEquallOntop.append(doubleStackSpaceNotEquall[subIndex])
            for crate in crate_instances:
                if crate.id == doubleStackSpaceNotEquall[subIndex + 1].id :
                    crate.set_tracking_number(crate.get_tracking_number() + " x " + doubleStackSpaceNotEquall[subIndex].get_tracking_number())
            subIndex += 2
        removeList = doubleStackSpaceEqualOnTop + doubleStackSpaceNotEquallOntop
        crate_instances_use = [crate for crate in crate_instances if crate not in removeList]
    else:
        crate_instances_use = crate_instances
    print(len(crate_instances_use))

    """
    Khúc này là để bỏ từ CrateRow list vào Item list, hiện chỉ dùng đúng width và length chứ ko có ailse, sẽ thêm sau nếu cần
    sau này sau khi đã có xong algorythm để Stack thì thêm vào sau cái này để xử lý cái list maximal 
    """
    maximal = [] 
    for crate in crate_instances_use:
        if (crate.double == "Yes") :
            maximal.append(Item(round(crate.width, 2) + 0.9, round(crate.length, 2) + 0.9, str(crate.id)))
        else :
            maximal.append(Item(round(crate.width, 2) + 0.5, round(crate.length, 2) + 0.5, str(crate.id)))
   
    globalItemList.extend(maximal)
    global wsaaLoop, indicator
    indicator = 0
    wsaaLoop = int(pollRow)
    if wsaaLoop != 0:
        algorythmExecute(maximal, binWidth, pollPosition + 0.25, crate_instances_use, crate_instances)
    else:
        algorythmExecute(maximal, binWidth, binMaxLength, crate_instances_use, crate_instances)
    print('length of used crate: '+str(len(cordinateList)))
    print('Num of crate each row: '+str(numOfCrate))
    drawBinsWithMultipleRows(cordinateList, crate_instances, binWidth, binMaxLength)
    honeycombRate = calculateHoneycombWithMultiplePoll(cordinateList, binWidth, binMaxLength, crate_instances_use)

    print('Crate instance use: '+str(len(crate_instances_use)))
    print('Too_cr length: '+str(len(tool_cr)))
    dict = {'Crate':tool_cr,'Label':tool_label, 'width': tool_w, 'Length': tool_l, 'x':x_list, 'y':y_list, 'Rotation': tool_rotation, 'Zone':zone, 'Double Stack':doubleStackList}
    df_statistic = pd.DataFrame(dict)
    df_statistic.to_csv('statistic.csv')
    print(len(crate_instances_use))
    usableSpace = (float(l) * float(w)) - (float(l) * float(w))*float(honeycombRate) / 100 - sum(crateItem.area for crateItem in crate_instances_use)
    rowsUpper[0][4] = honeycombRate
    rowsUpper[0][5] = usableSpace
    rowsUpper[0][6] = len(crate_instances)
    rowsUpper[0][7] = len(doubleStackFull)
    rows = rowsUpper[0:1]
    np.savetxt("algo.csv", 
           rows,
           delimiter =", ", 
           fmt ='% s')
   
    dict_poll = {'PollX':poll_x, 'PollY':poll_y}
    df_poll = pd.DataFrame(dict_poll)
    df_poll.to_csv('poll.csv')

    dict_ailse = {'AilseX':ailse_x, 'AilseY':ailse_y, 'AilseW':ailse_w, 'AilseL':ailse_l}
    df_ailse = pd.DataFrame(dict_ailse)
    df_ailse.to_csv('ailse.csv')
                

