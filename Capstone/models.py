from .import db,ma
from Capstone.__init__ import create_app
import datetime


#Class database
# table store user information including password
class User(db.Model):
    __tablename__ = 'users_auth'
    user_id = db.Column(db.String(255), unique=True, primary_key = True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(30))
    admin = db.Column(db.Boolean)

    def __init__(self, user_id, username, email, password, role, admin):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.admin = admin

class History(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    description = db.Column(db.Text())
    user_id = db.Column(db.Text())
    dattime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,description,user_id,dattime):
        self.description=description
        self.user_id=user_id
        self.dattime=dattime


class ProjectHistory(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    project_id=db.Column(db.Integer)
    description = db.Column(db.Text())
    user_id = db.Column(db.Text())
    dattime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,project_id,description,user_id,dattime):
        self.project_id=project_id
        self.description=description
        self.user_id=user_id
        self.dattime=dattime

class ZoneHistory(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    zone_id=db.Column(db.Integer)
    description = db.Column(db.Text())
    user_id = db.Column(db.Text())
    dattime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,zone_id,description,user_id,dattime):
        self.zone_id=zone_id
        self.description=description
        self.user_id=user_id
        self.dattime=dattime

class Layouts(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    zone_id = db.Column(db.Integer)
    crate_label = db.Column(db.Text())
    tracking =db.Column(db.Text())
    stacked = db.Column(db.Text())
    width= db.Column(db.Float())
    length= db.Column(db.Float())
    x= db.Column(db.Float())
    y=db.Column(db.Float())
    rotation=db.Column(db.Boolean())

    def __init__(self,tracking,crate_label,stacked,width,length,zone_id,x,y,rotation):
        self.tracking=tracking
        self.crate_label=crate_label
        self.zone_id=zone_id
        self.stacked=stacked
        self.width=width
        self.length=length
        self.x=x
        self.y=y
        self.rotation=rotation





class ZoneStatistics(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    zone_id=db.Column(db.Integer)
    total_space= db.Column(db.Float)
    total_used=db.Column(db.Float)
    usable=db.Column(db.Float)
    honeycomb=db.Column(db.Float)
    honeycomb_rate=db.Column(db.Float)
    number_crates = db.Column(db.Integer)
    number_stacks = db.Column(db.Integer)
    number_singles = db.Column(db.Integer)

    def __init__(self,zone_id,total_space,total_used,usable,honeycomb,honeycomb_rate,number_crates,number_stacks,number_singles):
        self.zone_id=zone_id
        self.total_space=total_space
        self.total_used=total_used
        self.usable=usable
        self.honeycomb=honeycomb
        self.honeycomb_rate=honeycomb_rate
        self.number_crates = number_crates
        self.number_stacks = number_stacks
        self.number_singles = number_singles

class Playground(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    zone_id = db.Column(db.Integer)
    crate_label = db.Column(db.Text())
    tracking =db.Column(db.Text())
    stacked = db.Column(db.Text())
    width= db.Column(db.Float())
    length= db.Column(db.Float())
    x= db.Column(db.Float())
    y=db.Column(db.Float())
    rotation=db.Column(db.Boolean())

    def __init__(self,tracking,crate_label,stacked,width,length,zone_id,x,y,rotation):
        self.tracking=tracking
        self.crate_label=crate_label
        self.zone_id=zone_id
        self.stacked=stacked
        self.width=width
        self.length=length
        self.x=x
        self.y=y
        self.rotation=rotation

class Pole(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    zone_id = db.Column(db.Integer)
    width= db.Column(db.Float())
    length= db.Column(db.Float())
    x= db.Column(db.Float())
    y=db.Column(db.Float())

    def __init__(self,zone_id,width,length,x,y):
        self.zone_id=zone_id
        self.width=width
        self.length=length
        self.x=x
        self.y=y

class Ailse(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    zone_id = db.Column(db.Integer)
    width= db.Column(db.Float())
    length= db.Column(db.Float())
    x= db.Column(db.Float())
    y=db.Column(db.Float())

    def __init__(self,zone_id,width,length,x,y):
        self.zone_id=zone_id
        self.width=width
        self.length=length
        self.x=x
        self.y=y

# table store invalid token which will be store when logout
class Chart(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    project_id = db.Column(db.Integer)
    zone_id = db.Column(db.Integer)
    honeycomb = db.Column(db.String(255))
    datime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,project_id,zone_id,honeycomb,datime):
        self.project_id=project_id
        self.zone_id=zone_id
        self.honeycomb=honeycomb
        self.datime=datime

# table store invalid token which will be store when logout
class Token(db.Model):
    __tablename__ = 'user_token_black_list'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    user_id = db.Column(db.String(255))
    token = db.Column(db.String(255), unique=True)
    #create_data = db.Column(db.String(255), unique=True)

