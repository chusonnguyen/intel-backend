from email.policy import default
from flask import Flask, jsonify, request,Blueprint
from flask_cors import CORS, cross_origin
import datetime
from . import db, ma
import MySQLdb
from . import mysql
import json
from .wraps import token_required
from .models import Token, User, ProjectHistory
from .__init__ import create_app
from sqlalchemy import create_engine


project = Blueprint('project', __name__)

db.create_all(app = create_app())

class Projects(db.Model):
    project_id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Text())
    project_name = db.Column(db.Text())
    project_type = db.Column(db.Text())
    address = db.Column(db.Text())
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow)


    def __init__(self,user_id,project_name,project_type,address,last_modified):
        self.user_id=user_id
        self.project_name=project_name
        self.project_type = project_type
        self.address=address
        self.last_modified=last_modified



class ProjectSchema(ma.Schema):
    class Meta:
        fields = ('project_id','user_id','project_name','project_type','address','last_modified')

project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)



@project.route('/projects',methods =['GET'])
@cross_origin()
@token_required
def get_projects(current_user, token):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT p.* , u.username as 'created_by' FROM projects p, users_auth u WHERE p.user_id = u.user_id ORDER BY project_id")
    all_projects = cursor.fetchall()
    cursor.close()
    print (all_projects)
    results = json.dumps(all_projects, default = str)
    return results

@project.route('/project/<id>',methods =['GET'])
@cross_origin()
@token_required
def get_project(current_user, token,id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT p.* , u.username as 'created_by' FROM projects p, users_auth u WHERE p.user_id= u.user_id AND p.project_id = %s;", [id])
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects, default= str)
    return results

@project.route('/zones/project=<id>',methods =['GET'])
@cross_origin()
@token_required
def post_details(current_user, token,id):
    user_id = current_user.user_id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT r.*, u.username AS created_by FROM refreshed_zones r, users_auth u WHERE r.user_id= u.user_id AND r.project_id = %s ORDER BY zone_id DESC;", [id])
    zones=cursor.fetchall()
    cursor.close()
    results = json.dumps(zones, default=str)
    return results


@project.route('/project/<id>',methods = ['PUT'])
@cross_origin()
@token_required
def update_project(current_user, token,id):
    project = Projects.query.get(id)

    project_name = request.json['project_name']
    project_type = request.json['project_type']
    address = request.json['address']

    project.project_name = project_name
    project.project_type = project_type
    project.address = address
    project.last_modified = datetime.datetime.utcnow()

    db.session.commit()
    return project_schema.jsonify(project)


@project.route('/project/<id>',methods=['DELETE'])
@cross_origin()
@token_required
def delete_project(current_user, token,id):
    project = Projects.query.get(id)
    db.session.delete(project)
    db.session.commit()
    return project_schema.jsonify(project)


@project.route('/projects',methods=['POST'])
@cross_origin()
@token_required
def add_project(current_user, token):
    req_data = request.get_json(force=False, silent=False, cache=True)
    user_id = current_user.user_id
    user_id = user_id
    project_name = req_data['project_name']
    project_type = req_data['project_type']
    address = req_data['address']


    projects = Projects(user_id,project_name,project_type,address,datetime.datetime.utcnow())

    db.session.add(projects)
    db.session.commit()
    return project_schema.jsonify(projects)