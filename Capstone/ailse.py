from flask import Flask, jsonify, request,Blueprint
from sqlalchemy import Integer

from Capstone.models import Playground,History,ZoneHistory, ZoneStatistics,Pole,Ailse
from . import db, ma
from . import mysql
import MySQLdb
import json
from .__init__ import create_app
from .wraps import token_required
from flask_cors import cross_origin
import datetime

ailse = Blueprint('ailse', __name__)


db.create_all(app = create_app())

class AilseSchema(ma.Schema):
    class Meta:
        fields = ('id','zone_id','width','length','x','y')

ailse_schema = AilseSchema()
ailses_schema = AilseSchema(many=True)

@ailse.route('/<zoneid>',methods =['GET'])
@cross_origin()
@token_required
def getAilses(current_user, token,zoneid):
    # user_id = current_user.user_id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT p.id, p.width, p.length, p.x, p.y FROM ailse p WHERE zone_id = %s;", [zoneid])
    zones=cursor.fetchall()
    cursor.close()
    results = json.dumps(zones, default=str)
    return results