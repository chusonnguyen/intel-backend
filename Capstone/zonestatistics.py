from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import json
from .__init__ import create_app
from .wraps import token_required
from .models import ZoneStatistics


zonestatistics = Blueprint('zonestatistics', __name__)

db.create_all(app = create_app())

class ZoneStatisticsSchema(ma.Schema):
    class Meta:
        fields = ('id','zone_id','total_space','total_used','usable','honeycomb','honeycomb_rate', 'number_crates', 'number_stacks', 'number_singles')

ZoneStatistics_schema = ZoneStatisticsSchema()

@zonestatistics.route('/zoneid=<id>',methods =['GET'])
@token_required
def get_layoutbyid(current_user, token,id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT u.username as created_by, z.* FROM zone_statistics z, refreshed_zones r, users_auth u  WHERE r.user_id = u.user_id AND z.zone_id = r.zone_id AND z.zone_id = %s;",[id])
    all_projects = cursor.fetchall()
    cursor.close()
    if all_projects == ():
        print("go here")
        return jsonify({'Hello': 'Null body'})
    #results = json.dumps(all_projects)s
    return jsonify({'statistic':all_projects})