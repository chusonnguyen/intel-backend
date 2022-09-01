from flask import Blueprint, render_template, request, Flask, jsonify
import pandas as pd
from . import mysql
from .procespool import Crate, main
from .rowProcessPool import CrateRow,mainRow
import json
from flask_cors import CORS, cross_origin
import os
import urllib.request
from werkzeug.utils import secure_filename
from flask import current_app as app
from .wraps import token_required
from . import db
from sqlalchemy import create_engine
import MySQLdb
from .models import Layouts,ZoneStatistics,Playground,ZoneHistory,History,Pole,Ailse,Chart
import datetime


views = Blueprint('views', __name__)
ALLOWED_EXTENSIONS = set(['xlsx'])



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/', methods=['GET'])
def home():
    return jsonify('healthcheck')
    
@views.route('/upload/<zoneid>', methods=['POST'])
@cross_origin()
@token_required
def upload_file(current_user, token,zoneid):
    removeFiles()
    cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor2.execute("DELETE FROM `pole` WHERE zone_id = %s", [zoneid])
    cursor2.execute("DELETE FROM `ailse` WHERE zone_id = %s", [zoneid])
    cursor2.execute("DELETE FROM `zone_statistics` WHERE zone_id = %s", [zoneid])
    cursor2.execute("DELETE FROM `layouts` WHERE zone_id = %s", [zoneid])
    cursor2.execute("DELETE FROM `playground` WHERE zone_id = %s", [zoneid])

    mysql.connection.commit()
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in request'})
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #history zone
    cursor.execute('SELECT zone_name FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    zname=cursor.fetchone()
    zonename=zname.get('zone_name')
    Zonehistory = ZoneHistory(zoneid,"Upload New Layout for Zone: "+zonename,current_user.user_id,datetime.datetime.utcnow())
    history = History("Upload New Layout for Zone: "+zonename,current_user.user_id,datetime.datetime.utcnow())
    db.session.add(Zonehistory)
    db.session.add(history)
    db.session.commit()
    #width 
    cursor.execute('SELECT width FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    width=cursor.fetchone()
    #length
    cursor.execute('SELECT length FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    length=cursor.fetchone()
    #total poll
    cursor.execute('SELECT totalPoll FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    totalPoll=cursor.fetchone()
    #poll row
    cursor.execute('SELECT pollRow FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    pollRow=cursor.fetchone()
    #poll width
    cursor.execute('SELECT pollW FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    pollW=cursor.fetchone()
    #poll length
    cursor.execute('SELECT pollL FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    pollL=cursor.fetchone()
    #poll X
    cursor.execute('SELECT pollX FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    pollX=cursor.fetchone()
    #poll Y
    cursor.execute('SELECT pollY FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    pollY=cursor.fetchone()
    #poll Gap
    cursor.execute('SELECT pollGap FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    pollGap=cursor.fetchone()
    #poll row gap
    cursor.execute('SELECT pollRowGap FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    pollRowGap=cursor.fetchone()

    cursor.close()
    w=int(width.get('width'))
    l=int(length.get('length'))
    totalPoll = int(totalPoll.get('totalPoll'))
    pollRow = int(pollRow.get('pollRow'))
    pollW = float(pollW.get('pollW'))
    pollL = float(pollL.get('pollL'))
    pollX = float(pollX.get('pollX'))
    pollY = float(pollY.get('pollY'))
    pollGap = float(pollGap.get('pollGap'))
    pollRowGap = float(pollRowGap.get('pollRowGap'))


    file = request.files['file']
    # w = request.values['w']
    # l = request.values['l']
    print(w)
    print(l)
    print(totalPoll)
    print(pollRow)
    print(pollW)
    print(pollL)
    print(pollX)
    print(pollY)
    print(pollRowGap)
    # projectId = request.values['project_id']
    zoneId = request.values['zone_id']

    if file.filename == '':
        return jsonify({'message' : 'No file selected for uploading'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        pollRow = int(pollRow)
        if pollRow == 1: 
            main(load_file(get_file()), w, l, totalPoll, pollRow, pollW, pollL, pollX, pollY, pollGap,pollRowGap)
            saveDB(load_file(get_file()), zoneId,w,l)
        else:
            mainRow(load_file(get_file()), w, l, totalPoll, pollRow, pollW, pollL, pollX, pollY, pollGap,pollRowGap)
            saveDBRow(load_file(get_file()), zoneId,w,l)
        return jsonify({'message' : 'File successfully uploaded'})
    
    return jsonify({'message' : 'Allowed file types is xlsx'})

@views.route('/get_file', methods=['GET'])
@cross_origin()
@token_required
def show_file_content(current_user,token):
    df = pd.read_csv('C:/Users/Tun/Desktop/Git/statistic.csv')
    #df = df[df['Occupied space'].notna()]
    #colList = ["Occupied space", "Tool sqm", "Ailse", "Length", "Width", "Height", "Weights", "Crate Label", "Double stack"]
    #df_new = df[["Occupied space", "Tool sqm", "Ailse", "Length", "Width", "Height", "Weights", "Crate Label", "Double stack"]]
    json_str = df.to_json()

    #json_str = jsonify(df_new)
    print(json_str)
    x = {
        "query1": json_str,
    }
    return json_str

class Statistics:
    def __init__(self, trackingNumber, crateLabel: str, x, y, rotation,stacked):
        self.trackingNumber = trackingNumber
        self.crateLabel = crateLabel
        self.x = x
        self.y = y
        self.rotation = rotation
        self.stacked = stacked

def removeFiles():
    if os.path.exists("algo.csv"):
        os.remove("algo.csv")
    if os.path.exists("statistic.csv"):
        os.remove("statistic.csv")
    if os.path.exists("poll.csv"):
        os.remove("poll.csv")
    if os.path.exists("ailse.csv"):
        os.remove("ailse.csv")
    else:
        print('File does not exists')

def saveDBRow(df: pd.DataFrame, zoneId,w,l):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorPoll = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorProject = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #Upload file o day
    df_statistic = pd.read_csv("statistic.csv")
    trackingNumber = df_statistic['Crate'].tolist()
    label = df_statistic['Label'].tolist()
    Xaxis = df_statistic['x'].tolist()
    Yaxis = df_statistic['y'].tolist()
    rotation = df_statistic['Rotation'].tolist()
    stacked = df_statistic['Double Stack'].tolist()

    statistic = []
    for index in range(len(label)):
        if stacked[index] == "Yes":
            labelList = label[index].split("x")
            trackingList = trackingNumber[index].split("x")
            statistic.append(Statistics(trackingNumber[index], labelList[0].strip(), Xaxis[index], Yaxis[index], rotation[index],stacked[index] ))
            statistic.append(Statistics(trackingNumber[index], labelList[1].strip(), Xaxis[index], Yaxis[index], rotation[index],stacked[index] ))
        else:
            statistic.append(Statistics(trackingNumber[index], label[index], Xaxis[index], Yaxis[index], rotation[index],stacked[index] ))
           
    #Global statistics ben FE 
    cursor.execute("SELECT count(*) as count FROM `zone_statistics` WHERE zone_id = %s", [zoneId])
    count=cursor.fetchone() #bien check coi data ton tai chua
    cursorPoll.execute("SELECT pollW, pollL FROM refreshed_zones WHERE zone_id = %s",[zoneId])
    pollWL = cursorPoll.fetchone()
    pollW = pollWL['pollW']
    pollL = pollWL['pollL']
    print("PollWL")
    print(pollWL)

    
    cursor.close()
    #save ailse to db 
    df_ailse = pd.read_csv("ailse.csv")
    ailseX = df_ailse['AilseX'].tolist()
    ailseY = df_ailse['AilseY'].tolist()
    ailseW = df_ailse['AilseW'].tolist()
    ailseL = df_ailse['AilseL'].tolist()
    for index in range(len(ailseX)):
        ailseData = Ailse(zoneId, ailseW[index], ailseL[index], ailseX[index], ailseY[index])
        db.session.add(ailseData)
        db.session.commit()
                
    # if count['count'] == 0:
    df_layoutstat = pd.read_csv("algo.csv", header=None)
    if pollW != 0 or pollL != 0 :
        #save poll to db
        df_poll = pd.read_csv("poll.csv")
        zoneId = zoneId
        Xaxis = df_poll['PollX'].tolist()
        Yaxis = df_poll['PollY'].tolist()
        for index in range(len(Xaxis)):
            poleData = Pole(zoneId, pollW, pollL, Xaxis[index], Yaxis[index])
            db.session.add(poleData)
            db.session.commit()

    
    
        

    total_space= float(w)*float(l)
    usable = df_layoutstat[5][0]
    honeycomb_rate = df_layoutstat[4][0]
    honeycomb=(float(honeycomb_rate)/100)*total_space
    total_used= total_space-float(usable)-honeycomb
    numberCrate = df_layoutstat[6][0]
    numberDouble = df_layoutstat[7][0]
    numberSingle = numberCrate - numberDouble
    thisStat=ZoneStatistics(zoneId,total_space,total_used,usable,honeycomb,honeycomb_rate, numberCrate, numberDouble, numberSingle)
    db.session.add(thisStat)
    cursorProject.execute("SELECT project_id FROM `refreshed_zones` WHERE zone_id = %s", [zoneId])
    project_id=cursorProject.fetchone() 
    cursorProject.close()
    projectID = int(project_id.get('project_id'))
    currentTime = datetime.datetime.utcnow()
    thisChart = Chart(projectID,zoneId,honeycomb_rate,currentTime)
    db.session.add(thisChart)
    db.session.commit()

    df = df[df['Occupied space'].notna()]
    colList = ["Occupied space", "Tool sqm", "Ailse", "Length", "Width", "Height", "Weights", "Crate Label", "Double stack"]
    dataColName = df.columns.tolist()
    indexList = []
    for colName in colList:
        indexList.append(dataColName.index(colName))
    crateInfoList = df.values.tolist()

    crate_instances = [] # Danh sách các Crate sau khi đọc xong
    for crateInfo in crateInfoList:
        crate_instances.append(CrateRow(*[crateInfo[index] for index in indexList]))
    
    for row in crate_instances:
        statis = [stat for stat in statistic if str(stat.crateLabel) == str(row.id)]
        #print(len(statis) + ' ' +str(row.id))
        if (len(statis) != 0):
            print(statis[0].trackingNumber)
            layout = Layouts(statis[0].trackingNumber,statis[0].crateLabel ,statis[0].stacked ,row.width, row.length, zoneId, statis[0].x, statis[0].y,statis[0].rotation)
            playground=Playground(statis[0].trackingNumber,statis[0].crateLabel ,statis[0].stacked ,row.width, row.length, zoneId, statis[0].x, statis[0].y,statis[0].rotation)
            db.session.add(layout)
            db.session.add(playground)
            #cursor.execute("INSERT INTO layouts (zone_id, crate_label, stacked, width, length, x, y) VALUES (%s,%s,%s,%s,%s,%s,%s)", [2,3,4,5,6,0,0])
            db.session.commit()

    return jsonify({'message' : 'Saved to database'})
    
        
        




def saveDB(df: pd.DataFrame, zoneId,w,l):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorPoll = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorProject= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # new_df = df[['Crate Label', 'Double stack', 'Length', 'Width']]
    # new_df = new_df.rename(columns={'Crate Label': 'crate_label','Double stack':'double_stack','Width': 'width','Length': 'length'})
    # new_df['zone_id'] = zoneId

    # new_df['crate_label'] = str(new_df['crate_label'])
    # new_df['double_stack'] = str(new_df['double_stack'])

    # print('string value of df: ' + str(new_df['crate_label'][0]))
    
    #Upload file o day
    df_statistic = pd.read_csv("statistic.csv")
    trackingNumber = df_statistic['Crate'].tolist()
    label = df_statistic['Label'].tolist()
    Xaxis = df_statistic['x'].tolist()
    Yaxis = df_statistic['y'].tolist()
    rotation = df_statistic['Rotation'].tolist()
    stacked = df_statistic['Double Stack'].tolist()

    statistic = []
    for index in range(len(label)):
        if stacked[index] == "Yes":
            labelList = label[index].split("x")
            trackingList = trackingNumber[index].split("x")
            statistic.append(Statistics(trackingList[0].strip(), labelList[0].strip(), Xaxis[index], Yaxis[index], rotation[index],stacked[index] ))
            statistic.append(Statistics(trackingList[1].strip(), labelList[1].strip(), Xaxis[index], Yaxis[index], rotation[index],stacked[index] ))
        else:
            statistic.append(Statistics(trackingNumber[index], label[index], Xaxis[index], Yaxis[index], rotation[index],stacked[index] ))
    
    cursorPoll.execute("SELECT pollW, pollL FROM refreshed_zones WHERE zone_id = %s",[zoneId])
    pollWL = cursorPoll.fetchone()
    pollW = pollWL['pollW']
    pollL = pollWL['pollL']
    print("pollW PollL")
    print(pollW)
    print(pollL)
    #Global statistics ben FE 
    cursor.execute("SELECT count(*) as count FROM `zone_statistics` WHERE zone_id = %s", [zoneId])
    count=cursor.fetchone()
    cursor.close()
    print('This is count')
    print(type(count))
    print(count)
    if count['count'] == 0:
        df_poll = pd.read_csv("poll.csv")
        zoneId = zoneId
        Xaxis = df_poll['PollX'].tolist()
        Yaxis = df_poll['PollY'].tolist()
        for index in range(len(Xaxis)):
            poleData = Pole(zoneId, pollW, pollL, Xaxis[index], Yaxis[index])
            db.session.add(poleData)
            db.session.commit()
            

        df_layoutstat = pd.read_csv("algo.csv")
        for index in range(len(df_layoutstat)):
            thisRow=df_layoutstat.iloc[index]
            total_space= float(w)*float(l)
            usable = thisRow[5]
            honeycomb_rate = thisRow[4]
            honeycomb=(float(honeycomb_rate)/100)*total_space
            total_used= total_space-float(usable)-honeycomb
            numberCrate = thisRow[6]
            numberDouble = thisRow[7]
            numberSingle = numberCrate - numberDouble
            thisStat=ZoneStatistics(zoneId,total_space,total_used,usable,honeycomb,honeycomb_rate, numberCrate, numberDouble, numberSingle)
            cursorProject.execute("SELECT project_id FROM `refreshed_zones` WHERE zone_id = %s", [zoneId])
            project_id=cursorProject.fetchone() 
            projectID = int(project_id.get('project_id'))
            currentTime = datetime.datetime.utcnow()
            thisChart = Chart(projectID,zoneId,honeycomb_rate,currentTime)
            db.session.add(thisChart)
            db.session.add(thisStat)
            db.session.commit()

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
        
        for row in crate_instances:
            statis = [stat for stat in statistic if str(stat.crateLabel) == str(row.id)]
            #print(len(statis) + ' ' +str(row.id))
            layout = Layouts(statis[0].trackingNumber,statis[0].crateLabel ,statis[0].stacked ,row.width, row.length, zoneId, statis[0].x, statis[0].y,statis[0].rotation)
            playground=Playground(statis[0].trackingNumber,statis[0].crateLabel ,statis[0].stacked ,row.width, row.length, zoneId, statis[0].x, statis[0].y,statis[0].rotation)
            db.session.add(layout)
            db.session.add(playground)
            #cursor.execute("INSERT INTO layouts (zone_id, crate_label, stacked, width, length, x, y) VALUES (%s,%s,%s,%s,%s,%s,%s)", [2,3,4,5,6,0,0])
            db.session.commit()
        return jsonify({'message' : 'Saved to database'})
    else:
        print('Delete')
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute("DELETE FROM `zone_statistics` WHERE zone_id = %s", [zoneId])
        cursor2.execute("DELETE FROM `layouts` WHERE zone_id = %s", [zoneId])
        cursor2.execute("DELETE FROM `playground` WHERE zone_id = %s", [zoneId])
        mysql.connection.commit()
        df_layoutstat = pd.read_csv("algo.csv")
        for index in range(len(df_layoutstat)):
            thisRow=df_layoutstat.iloc[index]
            total_space= float(w)*float(l)
            usable = thisRow[5]
            honeycomb_rate = thisRow[4]
            honeycomb=(float(honeycomb_rate)/100)*total_space
            total_used= total_space-float(usable)-honeycomb
            number_crates =thisRow[6]
            number_stacks = thisRow[7]
            number_singles = number_crates - number_stacks

            thisStat=ZoneStatistics(zoneId,total_space,total_used,usable,honeycomb,honeycomb_rate, number_crates, number_stacks, number_singles)
            db.session.add(thisStat)
            db.session.commit()

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
        
        for row in crate_instances:
            statis = [stat for stat in statistic if str(stat.crateLabel) == str(row.id)]
            layout = Layouts(statis[0].trackingNumber,statis[0].crateLabel ,statis[0].stacked ,row.width, row.length, zoneId, statis[0].x, statis[0].y,statis[0].rotation)
            playground = Playground(statis[0].trackingNumber,statis[0].crateLabel ,statis[0].stacked ,row.width, row.length, zoneId, statis[0].x, statis[0].y,statis[0].rotation)
            db.session.add(layout)
            db.session.add(playground)
            #cursor.execute("INSERT INTO layouts (zone_id, crate_label, stacked, width, length, x, y) VALUES (%s,%s,%s,%s,%s,%s,%s)", [2,3,4,5,6,0,0])
            db.session.commit()
    
    cursorProject.close()
    cursor2.close()
    return jsonify({'message' : 'Saved to database'})

def get_file():
    filename = []
    dir_path = app.config['UPLOAD_FOLDER']
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            filename.append(path)
    return filename[0]

def check_file_type(file):
    name, extension = os.path.splitext(file)
    if extension == '.xlsx':
        return extension
    if extension == '.csv':
        return extension
    return print('fail to check file type')
    
def load_file(file):
    if check_file_type(file) == '.xlsx':
        df = pd.read_excel(app.config['UPLOAD_FOLDER'] + "/" + file)
        return df
    if check_file_type(file) == '.csv':
        df = pd.read_csv(app.config['UPLOAD_FOLDER'] + "/" + file)
        return df
    return print("invalid file type")

