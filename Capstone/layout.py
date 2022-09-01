from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import json
from .__init__ import create_app
from .models import Layouts

layout = Blueprint('layout', __name__)

db.create_all(app = create_app())

class LayoutSchema(ma.Schema):
    class Meta:
        fields = ('id','tracking','crate_label','stacked','width','zone_id','length','x','y','rp')

layout_schema = LayoutSchema()
layouts_schema = LayoutSchema(many=True)

@layout.route('/',methods =['GET'])
def get_layouts():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT l.* FROM layouts l;")
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results

@layout.route('/<zoneid>',methods=['POST'])
def add_layout(zoneid):
    req_data = request.get_json(force=False, silent=False, cache=True)
    crate_label = req_data['crate_label']
    stacked = req_data['stacked']
    zone_id = req_data[zone_id]
    width = req_data['width']
    length = req_data['length']
    x = req_data['x']
    y = req_data['y']

    layout = Layouts(crate_label,stacked,zone_id,width,y,length,x)
    db.session.add(layout)
    db.session.commit()
    return layout_schema.jsonify(layout)

@layout.route('/<id>',methods = ['PUT'])
def update_layout(id):
    layout = Layouts.query.get(id)

    honeycomb = request.json['honeycomb']
    total_space = request.json['total_space']
    usable = request.json['usable']

    layout.honeycomb = honeycomb
    layout.total_space = total_space
    layout.usable = usable

    db.session.commit()
    return layout_schema.jsonify(layout)

@layout.route('/zoneid=<id>',methods =['GET'])
def get_layoutbyid(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT l.* FROM layouts l WHERE l.zone_id = %s;",[id])
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results

