from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import json
from .wraps import token_required
from flask_cors import cross_origin
from .__init__ import create_app
import datetime
from .models import History, Token, User, ProjectHistory


refreshedzone = Blueprint('refreshedzone', __name__)

db.create_all(app = create_app())

class RefreshedZones(db.Model):
    zone_id = db.Column(db.Integer,primary_key=True)
    project_id = db.Column(db.Integer)
    zone_name = db.Column(db.Text())
    zone_type = db.Column(db.Text())
    width=db.Column(db.Float())
    length=db.Column(db.Float())
    totalPoll = db.Column(db.Integer)
    pollRow = db.Column(db.Integer)
    pollX = db.Column(db.Float)
    pollY = db.Column(db.Float)
    pollW = db.Column(db.Float)
    pollL = db.Column(db.Float)
    pollGap = db.Column(db.Float)
    pollRowGap = db.Column(db.Float)
    user_id= db.Column(db.String(255))
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,project_id,zone_name,zone_type,width,length,totalPoll,pollRow,pollX,pollY,pollW,pollL,pollGap,pollRowGap,user_id,last_modified):
        self.project_id=project_id
        self.zone_name=zone_name
        self.zone_type=zone_type
        self.width=width
        self.length=length
        self.totalPoll = totalPoll
        self.pollRow = pollRow
        self.pollX = pollX
        self.pollY = pollY
        self.pollW = pollW
        self.pollL = pollL
        self.pollGap = pollGap
        self.pollRowGap = pollRowGap
        self.user_id=user_id
        self.last_modified=last_modified


class RefreshedZoneSchema(ma.Schema):
    class Meta:
        fields = ('zone_id','project_id','zone_name','zone_type','width','length','totalPoll','pollRow','pollX','pollY','pollW','pollL','pollGap','pollRowGap','user_id','last_modified')

refreshedzone_schema = RefreshedZoneSchema()
refreshedzones_schema = RefreshedZoneSchema(many=True)


@refreshedzone.route('/',methods =['GET'])
@cross_origin()
@token_required
def get_zonesall(current_user, token):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT r.* , u.username as 'created_by', p.project_name FROM refreshed_zones r, users_auth u, projects p  WHERE r.user_id= u.user_id AND r.project_id = p.project_id;")
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results

@refreshedzone.route('/zones',methods =['GET'])
@cross_origin()
@token_required
def get_zonesallr(current_user, token):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM refreshed_zones ORDER BY last_modified DESC;")
    all_zones1 = cursor.fetchall()
    cursor.execute("SELECT * FROM existed_zones ORDER BY last_modified DESC;")
    all_zones2 = cursor.fetchall()
    cursor.close()
    x = all_zones1 + all_zones2
    results = json.dumps(x,default=str)
    return results

#get dua theo id cua project
@refreshedzone.route('/zones/<projectid>',methods =['GET'])
@cross_origin()
@token_required
def get_zonesbyproject(current_user, token,projectid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT r.* , u.username as 'created_by', p.project_name FROM refreshed_zones r, users_auth u, projects p WHERE r.user_id= u.user_id AND r.project_id = p.project_id AND r.project_id = %s ORDER BY last_modified DESC;",[projectid])
    all_zone1 = cursor.fetchall()
    cursor.execute("SELECT r.* , u.username as 'created_by', p.project_name FROM existed_zones r, users_auth u, projects p WHERE  r.user_id= u.user_id AND r.project_id = p.project_id AND r.project_id = %s ORDER BY last_modified DESC;",[projectid])
    all_zone2 = cursor.fetchall()
    cursor.close()
    x=all_zone1 + all_zone2
    results = json.dumps(x)
    return results

#get theo user va projectid
@refreshedzone.route('/projectid=<projectid>/user=<userid>',methods =['GET'])
@cross_origin()
@token_required
def get_specificzones(current_user, token,projectid,userid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT r.* , u.username as 'created_by', p.project_name FROM refreshed_zones r, users_auth u, projects p  WHERE r.user_id= %s AND r.project_id=%s ORDER BY last_modified DESC;",(userid,projectid))
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results

#get dua theo id cua zone
@refreshedzone.route('refreshedzone/<id>',methods =['GET'])
@cross_origin()
@token_required
def get_zoneid(current_user, token,id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT r.* , u.username as 'created_by', p.project_name as 'project_name' FROM refreshed_zones r, users_auth u, projects p WHERE r.user_id= u.user_id AND r.project_id = p.project_id AND zone_id = %s ORDER BY last_modified DESC;",[id])
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects, default=str)
    return results


@refreshedzone.route('refreshedzone/<id>',methods = ['PUT'])
@cross_origin()
@token_required
def update_zone(current_user, token,id):
    refreshedzone = RefreshedZones.query.get(id)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT project_id FROM refreshed_zones WHERE zone_id = %s",[id])
    all_projects = cursor.fetchone()
    cursor.close()
    projectid= int(all_projects.get('project_id'))
    zone_name = request.json['zone_name']
    zone_type = request.json['zone_type']

    refreshedzone.zone_name = zone_name
    refreshedzone.zone_type = zone_type
    refreshedzone.last_modified = datetime.datetime.utcnow()

    Zonehistory = ProjectHistory(projectid,"Edited zone: "+zone_name,current_user.user_id,datetime.datetime.utcnow())
    db.session.add(Zonehistory)
    db.session.commit()
    return refreshedzone_schema.jsonify(refreshedzone)


@refreshedzone.route('/<id>',methods=['DELETE'])
@cross_origin()
@token_required
def delete_zone(current_user, token,id):
    refreshedzone = RefreshedZones.query.get(id)
    db.session.delete(refreshedzone)
    db.session.commit()
    return refreshedzone_schema.jsonify(refreshedzone)


@refreshedzone.route('/zones',methods=['POST'])
@cross_origin()
@token_required
def add_zone(current_user,token):
    print(current_user)
    req_data = request.get_json(force=False, silent=False, cache=True)
    project_id = req_data['project_id']
    zone_name = req_data['zone_name']
    zone_type = req_data['zone_type']
    width = req_data['width']
    print("width: " + width)
    length = req_data['length']
    totalPoll = req_data['totalPoll']
    pollRow = req_data['pollRow']
    pollX = req_data['pollX']
    pollY = req_data['pollY']
    pollW = req_data['pollW']
    pollL = req_data['pollL']
    pollGap = req_data['pollGap']
    pollRowGap = req_data['pollRowGap']
    last_modified = datetime.datetime.utcnow()
    user_id = current_user.user_id
    
    zones = RefreshedZones(project_id,zone_name,zone_type,width,length,totalPoll,pollRow,pollX,pollY,pollW,pollL,pollGap,pollRowGap,user_id,last_modified)
    Zonehistory = ProjectHistory(project_id,"Create zone: "+zone_name,user_id,last_modified)
    history = History("Create zone: "+zone_name,user_id,last_modified)
    db.session.add(zones)
    db.session.add(Zonehistory)
    db.session.add(history)
    db.session.commit()

    return refreshedzone_schema.jsonify(zones)