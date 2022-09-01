from flask import jsonify, request,Blueprint

from Capstone.models import Playground,History,ZoneHistory,Chart
from . import db, ma
from . import mysql
import MySQLdb
import json
from .__init__ import create_app
from .wraps import token_required
from flask_cors import cross_origin
import datetime

playground = Blueprint('playground', __name__)

class Rectangle:
    # Following method intitializes the values for object
    def __init__(self, min_x=0, max_x=0, min_y=0, max_y=0):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    #intersection_check method returns true if two rectangles intersects
    def intersection_check(self, other):
        if self.min_x > other.max_x or self.max_x < other.min_x:
            return False
        if self.min_y > other.max_y or self.max_y < other.min_y:
            return False
        return True

db.create_all(app = create_app())

class PlaygroundSchema(ma.Schema):
    class Meta:
        fields = ('id','tracking','crate_label','stacked','width','zone_id','length','x','y','rotation')

playground_schema = PlaygroundSchema()
playgrounds_schema = PlaygroundSchema(many=True)

#Outbound
@playground.route('/<zoneid>/<label>',methods=['DELETE'])
@cross_origin()
@token_required
def outbounce(current_user, token,zoneid,label):
    print(label)
    label = str(label).strip()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT stacked, width, length, x, y FROM `playground` where crate_label = %s', [label])
    crate = cursor.fetchone()
    stacked = str(crate.get('stacked'))
    width = float(crate.get('width'))
    length = float(crate.get('length'))
    x = float(crate.get('x'))
    y = float(crate.get('y'))
    
    #zone statistic
    cursor.execute('SELECT total_space, total_used, usable, number_crates, number_stacks, number_singles, honeycomb, honeycomb_rate from `zone_statistics` where zone_id = %s', [zoneid])
    zone_statistic = cursor.fetchone()
    totalSpace = float(zone_statistic.get('total_space'))
    totalUsed = float(zone_statistic.get('total_used'))
    usableSpace = float(zone_statistic.get('usable'))
    numberCrates = int(zone_statistic.get('number_crates'))
    numberStackes = int(zone_statistic.get('number_stacks'))
    numberSingles = int(zone_statistic.get('number_singles'))
    honeycomb = float(zone_statistic.get('honeycomb'))
    honeycombRate = float(zone_statistic.get('honeycomb_rate'))

    if stacked == 'Yes':
        widthItem = float(width) + 0.45
        lengthItem = float(length) + 0.45
        area = widthItem * lengthItem
        realArea =float(width) * float(length)
        ailseArea = area- realArea
        usableSpace = usableSpace + realArea
        honeycomb = honeycomb + ailseArea
        totalUsed = totalUsed - area
        honeycombRate = round(honeycomb / totalSpace, 4)*100
        numberCrates -= 1
        numberStackes -= 1
        cursor.execute('UPDATE `zone_statistics` SET `total_used`=%s,`usable`=%s,`number_crates`=%s,`number_stacks`=%s,`honeycomb`=%s,`honeycomb_rate`=%s WHERE zone_id = %s',[totalUsed,usableSpace,numberCrates,numberStackes,honeycomb,honeycombRate,zoneid])
        
        cursorProject= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorProject.execute("SELECT project_id FROM `refreshed_zones` WHERE zone_id = %s", [zoneid])
        project_id=cursorProject.fetchone() 
        cursorProject.close()
        projectID = int(project_id.get('project_id'))
        currentTime = datetime.datetime.utcnow()
        thisChart = Chart(projectID,zoneid,honeycombRate,currentTime)

        db.session.add(thisChart)
        db.session.commit()
        mysql.connection.commit()
    else:
        widthItem = float(width) + 0.25
        lengthItem = float(length) + 0.25
        area = widthItem * lengthItem
        realArea =float(width) * float(length)
        ailseArea = area- realArea
        usableSpace = usableSpace + realArea
        honeycomb = honeycomb + ailseArea
        totalUsed = totalUsed - area
        honeycombRate = round(honeycomb / totalSpace, 4)*100
        numberCrates -= 1
        numberSingles -= 1
        cursor.execute('UPDATE `zone_statistics` SET `total_used`=%s,`usable`=%s,`number_crates`=%s,`number_singles`=%s,`honeycomb`=%s,`honeycomb_rate`=%s WHERE zone_id = %s',[totalUsed,usableSpace,numberCrates,numberSingles,honeycomb,honeycombRate,zoneid])
        cursorProject= mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursorProject.execute("SELECT project_id FROM `refreshed_zones` WHERE zone_id = %s", [zoneid])
        project_id=cursorProject.fetchone() 
        cursorProject.close()
        projectID = int(project_id.get('project_id'))
        currentTime = datetime.datetime.utcnow()
        thisChart = Chart(projectID,zoneid,honeycombRate,currentTime)
        db.session.add(thisChart)
        db.session.commit()
        mysql.connection.commit()


    cursor.execute('DELETE FROM `playground` WHERE zone_id = %s AND crate_label = %s',[zoneid,label])
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT zone_name FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    zname=cursor.fetchone()
    zonename=str(zname.get('zone_name'))
    Zonehistory = ZoneHistory(zoneid,"Upload New Layout for Zone: "+zonename,current_user.user_id,datetime.datetime.utcnow())
    history = History("Upload New Layout for Zone: "+zonename,current_user.user_id,datetime.datetime.utcnow())
    db.session.add(Zonehistory)
    db.session.add(history)
    mysql.connection.commit()
    cursor.close()
    return jsonify({"Message":"item was successfully deleted"})

#inbound
@playground.route('/<zoneid>',methods=['POST'])
@cross_origin()
@token_required
def add_item(current_user, token, zoneid):
    req_data = request.get_json(force=False, silent=False, cache=True)
    # cursor3.execute("SELECT MAX(tracking) as tracking FROM playground l WHERE l.zone_id = %s;",[zoneid])
    # prows = cursor3.fetchone()
    tracking= req_data['tracking']
    user_id = current_user.user_id
    user_id = user_id
    zone_id = int(zoneid)
    crate_label = req_data['crate_label']
    stacked = str(req_data['stacked'])
    width = float(req_data['width'])
    length = float(req_data['length'])
    x = float(req_data['x'])
    y = float(req_data['y'])
    rotation = bool(req_data['rotation'])
    cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor2.execute('SELECT * FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    zone=cursor2.fetchone()
    zwidth=float(zone.get('width'))
    zlength=float(zone.get('length'))
    r2 = Rectangle(x,x+width,y,y+length)
    if r2.max_x > zwidth or r2.max_y > zlength:
        return jsonify({'message':'Out of area'}),500
    
    if stacked == 'No':
        rectList = []
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute("SELECT l.* FROM playground l WHERE l.zone_id = %s;",[zoneid])
        rows = cursor1.fetchall()
        
        for row in rows:
            rectList.append(Rectangle(min_x=float(row['x']), max_x=float(row['x'])+float(row['width']), min_y=float(row['y']), max_y=float(row['y'])+float(row['length'])))
        for r1 in rectList:
            if r1.intersection_check(r2) is True:
                return jsonify({'message':'overlap'}),500

        

    playground = Playground(tracking,crate_label,stacked,width,length,zone_id,x,y,rotation)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT zone_name FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    zname=cursor.fetchone()

    zonename=str(zname.get('zone_name'))
    #zone statistic
    cursor.execute('SELECT total_space, total_used, usable, number_crates, number_stacks, number_singles, honeycomb, honeycomb_rate from `zone_statistics` where zone_id = %s', [zoneid])
    zone_statistic = cursor.fetchone()
    totalSpace = float(zone_statistic.get('total_space'))
    totalUsed = float(zone_statistic.get('total_used'))
    usableSpace = float(zone_statistic.get('usable'))
    numberCrates = int(zone_statistic.get('number_crates'))
    numberStackes = int(zone_statistic.get('number_stacks'))
    numberSingles = int(zone_statistic.get('number_singles'))
    honeycomb = float(zone_statistic.get('honeycomb'))
    honeycombRate = float(zone_statistic.get('honeycomb_rate'))
    
    if stacked == 'Yes':
        widthItem = float(width) + 0.45
        lengthItem = float(length) + 0.45
        area = widthItem * lengthItem
        realArea = float(width) * float(length)
        ailseArea = area - realArea
        usableSpace = usableSpace - realArea
        honeycomb = honeycomb - ailseArea
        totalUsed = totalUsed + area
        honeycombRate = round(honeycomb / totalSpace, 4)*100
        numberCrates += 1
        numberStackes += 1
        cursor.execute('UPDATE `zone_statistics` SET `total_used`=%s,`usable`=%s,`number_crates`=%s,`number_stacks`=%s,`honeycomb`=%s,`honeycomb_rate`=%s WHERE zone_id = %s',[totalUsed,usableSpace,numberCrates,numberStackes,honeycomb,honeycombRate,zoneid])
        cursorProject= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorProject.execute("SELECT project_id FROM `refreshed_zones` WHERE zone_id = %s", [zoneid])
        project_id=cursorProject.fetchone() 
        cursorProject.close()
        projectID = int(project_id.get('project_id'))
        currentTime = datetime.datetime.utcnow()
        thisChart = Chart(projectID,zoneid,honeycombRate,currentTime)
        db.session.add(thisChart)
        db.session.commit()
        mysql.connection.commit()
    else :
        widthItem = float(width) + 0.25
        lengthItem = float(length) + 0.25
        area = widthItem * lengthItem
        realArea = float(width) * float(length)
        ailseArea = area - realArea
        usableSpace = usableSpace - realArea
        honeycomb = honeycomb - ailseArea
        totalUsed = totalUsed + area
        honeycombRate = round(honeycomb / totalSpace, 4)*100
        numberCrates += 1
        numberSingles += 1
        cursor.execute('UPDATE `zone_statistics` SET `total_used`=%s,`usable`=%s,`number_crates`=%s,`number_singles`=%s,`honeycomb`=%s,`honeycomb_rate`=%s WHERE zone_id = %s',[totalUsed,usableSpace,numberCrates,numberSingles,honeycomb,honeycombRate,zoneid])
        cursorProject= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursorProject.execute("SELECT project_id FROM `refreshed_zones` WHERE zone_id = %s", [zoneid])
        project_id=cursorProject.fetchone() 
        cursorProject.close()
        projectID = int(project_id.get('project_id'))
        currentTime = datetime.datetime.utcnow()
        thisChart = Chart(projectID,zoneid,honeycombRate,currentTime)
        db.session.add(thisChart)
        db.session.commit()
        mysql.connection.commit()

    cursor.close()
    cursor2.close()

    Zonehistory = ZoneHistory(zoneid,"Upload New Layout for Zone: "+zonename,user_id,datetime.datetime.utcnow())
    history = History("Upload New Layout for Zone: "+zonename,current_user.user_id,datetime.datetime.utcnow())
    db.session.add(Zonehistory)
    db.session.add(history)
    db.session.add(playground)
    db.session.commit()
    return playground_schema.jsonify(playground)

@playground.route('/zoneid=<id>',methods =['GET'])
@cross_origin()
@token_required
def playgroundbyid(current_user, token, id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT l.* FROM playground l WHERE l.zone_id = %s;",[id])
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results


#inbound update x y
@playground.route('update/<zoneid>',methods=['PUT'])
@cross_origin()
@token_required
def update_item(current_user, token, zoneid):
    req_data = request.get_json(force=False, silent=False, cache=True)
    user_id = current_user.user_id
    user_id = user_id
    zone_id = int(zoneid)
    crate_label = req_data['crate_label']

    x = float(req_data['x'])
    y = float(req_data['y'])

    print("zone id: "+ str(zone_id))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE playground p SET p.x = %s, p.y = %s WHERE p.crate_label= %s, p.zone_id = %s;",[x,y,crate_label,zoneid])
    mysql.connection.commit()


#save layout
#inbound update x y
@playground.route('savelayout/<zoneid>',methods=['POST'])
@cross_origin()
@token_required
def save_layout(current_user, token, zoneid):
    ratio = 35
    req_data = request.get_json(force=False, silent=False, cache=True)
    cursorProject= mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursorProject.execute("SELECT project_id FROM `refreshed_zones` WHERE zone_id = %s", [zoneid])
    project_id=cursorProject.fetchone() 
    cursorProject.close()
    projectID = int(project_id.get('project_id'))
    currentTime = datetime.datetime.utcnow()
    honeycombRate = req_data('honeycombRate')
    thisChart = Chart(projectID,zoneid,honeycombRate,currentTime)
    db.session.add(thisChart)
    db.session.commit()
    return jsonify(thisChart)

 
    