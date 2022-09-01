from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import json
from .wraps import token_required
from flask_cors import cross_origin
from .models import Token, User


dashboard = Blueprint('dashboard', __name__)


class Dashboards(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    project_id = db.Column(db.Integer)
    zone_id = db.Column(db.Integer)
    inboundrate = db.Column(db.Float)
    outboundrate = db.Column(db.Float)
    datime = db.Column(db.DateTime)

    def __init__(self,project_id,zone_id,inboundrate,outboundrate,datime):
        self.project_id = project_id
        self.zone_id=zone_id
        self.inboundrate=inboundrate
        self.outboundrate=outboundrate
        self.datime=datime


class DashboardSchema(ma.Schema):
    class Meta:
        fields = ('id','project_id','zone_id','inboundrate','outboundrate','datime')

dashboard_schema = DashboardSchema()
dashboards_schema = DashboardSchema(many=True)

@dashboard.route('/statistic/projectid=<id>',methods=['GET'])
@cross_origin()
@token_required
def get_statistic(current_user, token,id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select count(*) as total_zone, round(avg(z.usable), 2) as average_space, round(avg(z.honeycomb_rate),2) as average_rate, round((sum(z.usable) / sum(z.total_space)) * 100, 2) as usable_percent from zone_statistics z, refreshed_zones r where z.zone_id = r.zone_id and r.project_id = %s;",[id])
    first=cursor.fetchall()
    cursor.execute("SELECT COUNT(user_id) AS 'total_accessed', last_modified AS 'created_on' FROM projects group by user_id order by last_modified DESC;")
    second = cursor.fetchone()
    cursor.close()
    a = {
        "statistic":first,
        "detail":[second]
    }
    results = json.dumps(a, default=str)
    return results


@dashboard.route('zoneusable/projectid=<id>', methods=['GET'])
@cross_origin()
@token_required
def get_zone_usable(current_user,token, id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select r.zone_name AS 'zone_name', z.usable AS 'usable_space' from zone_statistics z, refreshed_zones r where z.zone_id = r.zone_id and r.project_id = %s;",[id])
    all_reports=cursor.fetchall()
    cursor.close()
    results = json.dumps(all_reports)
    return results

    
# @dashboard.route('/',methods=['POST'])
# @cross_origin()
# @token_required
# def add_report(current_user, token):
#     req_data = request.get_json(force=False, silent=False, cache=True)
#     project_id = req_data['project_id']
#     zone_id = req_data['zone_id']
#     inboundrate = req_data['inboundrate']
#     outboundrate = req_data['outboundrate']
#     datime = req_data['datime']

#     zones = Dashboards(project_id,zone_id,inboundrate,outboundrate,datime)
#     db.session.add(zones)
#     db.session.commit()
#     #add nhieu thi doi boundreport thanh boundreports
#     return dashboard_schema.jsonify(zones)

# @dashboard.route('/',methods =['GET'])
# @cross_origin()
# @token_required
# def get_report(current_user, token):
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT MONTH(datime) AS month, ROUND(AVG(inboundrate),2) AS 'INBOUND', ROUND(AVG(outboundrate),2) AS 'OUTBOUND' FROM boundreport WHERE YEAR(datime) = '2022' AND project_id = '1' group by MONTH(datime) ORDER BY MONTH(datime);")
#     all_reports=cursor.fetchall()
#     cursor.close()
#     results = json.dumps(all_reports)
#     return results

# @dashboard.route('/honeycomb',methods =['GET'])
# @cross_origin()
# @token_required
# def get_reporthoneycomb(current_user, token):
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT YEAR(datime) AS year, MONTH(datime) AS month, ROUND(avg(honeycomb),2) AS honeycomb FROM report WHERE YEAR(datime) = '2022' AND project_id = '1' group by MONTH(datime) ORDER BY MONTH(datime);;")
#     all_reports=cursor.fetchall()
#     cursor.close()
#     results = json.dumps(all_reports)
#     return results

# @dashboard.route('/honeycomb/year=<year>',methods =['GET'])
# @cross_origin()
# @token_required
# def get_honeyyear(current_user, token,year):
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT MONTH(datime) AS month, ROUND(avg(honeycomb),2) AS honeycomb FROM report WHERE YEAR(datime) = %s AND project_id = '1' group by MONTH(datime) ORDER BY MONTH(datime);;", [year])
#     all_reports=cursor.fetchall()
#     cursor.close()
#     results = json.dumps(all_reports)
#     return results

# @dashboard.route('/projectid=<id>',methods =['GET'])
# @cross_origin()
# @token_required
# def get_reports(current_user, token,id):
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT MONTH(datime) AS month, ROUND(AVG(inboundrate),2) AS 'inbound', ROUND(AVG(outboundrate),2) AS 'outbound' FROM boundreport WHERE YEAR(datime) = '2022' AND project_id = 1 group by MONTH(datime) ORDER BY MONTH(datime);")
#     all_reports=cursor.fetchall()
#     cursor.execute("SELECT MONTH(datime) AS month, ROUND(avg(honeycomb),2) AS honeycomb, ROUND(AVG(usable),2) AS usable FROM report where YEAR(datime) = '2022' AND project_id = 1 GROUP BY MONTH(datime) ORDER BY MONTH(datime);")
#     query2=cursor.fetchall()
#     cursor.close()
    
#     x = {
#         "boundreport": all_reports,
#         "statisticsreport": query2,
#     }

#     results = json.dumps(x)
#     return results

