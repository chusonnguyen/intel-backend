from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import datetime


statistic = Blueprint('statistic', __name__)


class Statistics(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    project_id = db.Column(db.Integer, nullable = False)
    zone_id = db.Column(db.Integer)
    algorithm = db.Column(db.String(20))
    heuristic = db.Column(db.String(25))
    honeycomb = db.Column(db.Float)
    usable = db.Column(db.Float)
    userid = db.Column(db.Integer)
    dattime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,project_id,zone_id,algorithm,heuristic,honeycomb,usable,user_id,dattime):
        self.project_id=project_id
        self.zone_id=zone_id
        self.algorithm=algorithm
        self.heuristic=heuristic
        self.honeycomb=honeycomb
        self.usable=usable
        self.user_id=user_id
        self.dattime=dattime
        

class StatisticSchema(ma.Schema):
    class Meta:
        fields = ('id','project_id','zone_id','algorithm','heuristic','honeycomb','usable','user_id','dattime')

statistic_schema = StatisticSchema()
statistics_schema = StatisticSchema(many=True)
