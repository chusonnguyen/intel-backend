from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import json
from Capstone.__init__ import create_app
import datetime
from .wraps import token_required


existedzone = Blueprint('existedzone', __name__)

db.create_all(app = create_app())
class ExistedZones(db.Model):
    zone_id = db.Column(db.Integer,primary_key=True)
    project_id = db.Column(db.Integer)
    zone_name = db.Column(db.Text())
    zone_type = db.Column(db.Text())
    width=db.Column(db.Float())
    length=db.Column(db.Float())
    user_id= db.Column(db.Text())
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,project_id,zone_name,zone_type,width,length,user_id,last_modified):
        self.project_id=project_id
        self.zone_name=zone_name
        self.zone_type=zone_type
        self.width=width
        self.length=length
        self.user_id=user_id
        self.last_modified=last_modified



class ExistedZoneSchema(ma.Schema):
    class Meta:
        fields = ('zone_id','project_id','zone_name','zone_type','width','length','user_id','last_modified')

existedzone_schema = ExistedZoneSchema()
existedzones_schema = ExistedZoneSchema(many=True)


@existedzone.route('/',methods =['GET'])
@token_required
def get_zones(current_user, token):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT e.* , CONCAT(u.firstname, ' ', u.lastname) as 'created_by', p.project_name FROM existed_zones e, users_auth u, projects p  WHERE e.user_id= u.user_id AND e.project_id = p.project_id;")
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results

@existedzone.route('/<id>',methods =['GET'])
@token_required
def post_details(current_user, token,id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT e.* , u.username, p.project_name as 'project_name' FROM existed_zones e, users_auth u, projects p WHERE e.user_id= u.user_id AND e.project_id = p.project_id AND zone_id = %s;",[id])
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results


@existedzone.route('/<id>',methods = ['PUT'])
@token_required
def update_zone(current_user, token,id):
    existedzone = ExistedZones.query.get(id)

    zone_name = request.json['zone_name']
    zone_type = request.json['zone_type']
    width= request.json['width']
    length=request.json['length']

    existedzone.zone_name = zone_name
    existedzone.zone_type = zone_type
    existedzone.width = width
    existedzone.length = length
    existedzone.last_modified= datetime.datetime.utcnow()

    db.session.commit()
    return existedzone_schema.jsonify(existedzone)


@existedzone.route('/<id>',methods=['DELETE'])
@token_required
def delete_zone(current_user, token,id):
    existedzone = ExistedZones.query.get(id)
    db.session.delete(existedzone)
    db.session.commit()
    return existedzone_schema.jsonify(existedzone)

@existedzone.route('/',methods=['POST'])
@token_required
def add_zone(current_user, token):
    req_data = request.get_json(force=False, silent=False, cache=True)
    project_id = req_data['project_id']
    zone_name = req_data['zone_name']
    zone_type = req_data['zone_type']
    width = req_data['width']
    length = req_data['length']
    user_id = req_data['user_id']
    last_modified = datetime.datetime.utcnow()



    zones = ExistedZones(project_id,zone_name,zone_type,width,length,user_id,last_modified)
    db.session.add(zones)
    db.session.commit()
    return existedzone_schema.jsonify(zones)