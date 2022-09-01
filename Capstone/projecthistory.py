from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import datetime
from Capstone.__init__ import create_app
from flask_cors import cross_origin
import json
from .wraps import token_required

projecthistory = Blueprint('projecthistory', __name__)

db.create_all(app = create_app())

#db.drop_all()

class ProjectHistorySchema(ma.Schema):
    class Meta:
        fields = ('id','project_id','description','user_id','dattime')

projecthistory_schema = ProjectHistorySchema()
projecthistories_schema = ProjectHistorySchema(many=True)

@projecthistory.route('/',methods=['GET'])
@cross_origin()
@token_required
def get_history(current_user, token):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT p.id,p.project_id, SUBSTRING(p.description, 14) AS 'project_name', p.description, p.user_id, u.username AS 'username', DATE_FORMAT(p.dattime, '%Y-%m-%d %T') as Time FROM project_history p, users_auth u, projects pro WHERE pro.project_id = p.project_id AND p.user_id = u.user_id ORDER BY dattime DESC;")
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results

@projecthistory.route('/<id>',methods=['GET'])
@cross_origin()
@token_required
def get_history_by_project(current_user, token,id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT p.id,p.project_id, SUBSTRING(p.description, 14) AS 'project_name', p.description, p.user_id, u.username AS 'username', DATE_FORMAT(p.dattime, '%%Y-%%m-%%d %%T') as Time FROM project_history p, users_auth u, projects pro WHERE pro.project_id = p.project_id AND p.user_id = u.user_id and p.project_id = %s ORDER BY dattime DESC;", [id])
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects, default=str)
    return results


@projecthistory.route('/modified',methods=['GET'])
@cross_origin()
@token_required
def get_modifiedhistory(current_user, token):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT user_id FROM `project_history` group by user_id order by dattime DESC;")
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results