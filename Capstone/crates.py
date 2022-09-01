from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import datetime
from .__init__ import create_app
import json

crates = Blueprint('crates', __name__)

db.create_all(app = create_app())

class Crates(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    layout_id =db.Column(db.Integer())
    crate_label = db.Column(db.Text())
    width = db.Column(db.Float())
    length = db.Column(db.Float())
    x = db.Column(db.Float())
    y= db.Column(db.Float())

    def __init__(self,layout_id,crate_label,width,length,x,y):
        self.crate_label=crate_label
        self.layout_id=layout_id
        self.width=width
        self.length=length
        self.x=x
        self.y=y
        


class CrateSchema(ma.Schema):
    class Meta:
        fields = ('id','layout_id','crate_label','width','length','x','y')

crate_schema = CrateSchema()
crates_schema = CrateSchema(many=True)


@crates.route('/crates',methods =['GET'])
def get_allcrates():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM crates c")
    all_projects = cursor.fetchall()
    cursor.close()
    print (all_projects)
    results = json.dumps(all_projects, default = str)
    return results