from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import datetime

from flask import current_app as app
from .__init__ import create_app

report = Blueprint('report', __name__)


class Reports(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    project_id = db.Column(db.Integer, nullable = False)
    honeycomb = db.Column(db.Float)
    usable = db.Column(db.Float)
    dattime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,project_id,honeycomb,usable,dattime):
        self.project_id=project_id
        self.honeycomb=honeycomb
        self.usable=usable
        self.dattime=dattime

db.create_all(app = create_app())
        

class ReportSchema(ma.Schema):
    class Meta:
        fields = ('id','project_id','honeycomb','usable','dattime')

report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)
