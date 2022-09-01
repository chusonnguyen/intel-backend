from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import datetime


cratetracking = Blueprint('cratetracking', __name__)


class CrateTrackings(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    project_id = db.Column(db.Integer, nullable = False)
    zone_id = db.Column(db.Integer)
    total = db.Column(db.Integer)
    dattime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,project_id,zone_id,total,dattime):
        self.project_id=project_id
        self.zone_id=zone_id
        self.total=total
        self.dattime=dattime
        


class CrateTrackingSchema(ma.Schema):
    class Meta:
        fields = ('id','project_id','zone_id','total','dattime')

cratetracking_schema = CrateTrackingSchema()
cratetrackings_schema = CrateTrackingSchema(many=True)
