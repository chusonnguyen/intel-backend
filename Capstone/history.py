from .models import History
from flask import Flask, jsonify, request,Blueprint
from . import db, ma
from . import mysql
import MySQLdb
import datetime
from Capstone.__init__ import create_app
from flask_cors import cross_origin
import json
from .wraps import token_required

history = Blueprint('history', __name__)

db.create_all(app = create_app())
#db.drop_all()

class HistorySchema(ma.Schema):
    class Meta:
        fields = ('id','description','user_id','dattime')
history_schema = HistorySchema()
histories_schema = HistorySchema(many=True)

@history.route('/',methods=['GET'])
@cross_origin()
@token_required
def get_history(current_user, token):
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT h.id, h.description, u.username AS user_id, DATE_FORMAT(h.dattime, '%Y-%m-%d %T') as Time FROM history h, users_auth u WHERE h.user_id = u.user_id order by h.dattime desc;")
    
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results







