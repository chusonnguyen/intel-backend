from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import datetime
from Capstone.__init__ import create_app
from flask_cors import cross_origin
import json
from .wraps import token_required

zonehistory = Blueprint('zonehistory', __name__)

db.create_all(app = create_app())


#db.drop_all()

class ZoneHistorySchema(ma.Schema):
    class Meta:
        fields = ('id','zone_id','description','user_id','dattime')

projecthistory_schema = ZoneHistorySchema()
projecthistories_schema = ZoneHistorySchema(many=True)


@zonehistory.route('/',methods=['GET'])
@cross_origin()
@token_required
def get_history(current_user, token):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id,zone_id, description, user_id, DATE_FORMAT(dattime, '%Y-%m-%d %T') as Time FROM zone_history ORDER BY dattime DESC;")
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results