from flask import Blueprint, request, jsonify, make_response
import uuid
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_cors import CORS, cross_origin


import jwt
from functools import wraps

from flask import current_app as app

from . import db
from . import ma
from .__init__ import create_app
from .wraps import token_required
from .models import Token, User

auth = Blueprint('auth', __name__)

#db.drop_all()
db.create_all(app = create_app())

class UserSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'username', 'email', 'password', 'role', 'admin')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class TokenSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'token')

token_schema = TokenSchema()
tokens_schema = TokenSchema(many=True)

@auth.route('/register', methods=['POST'])
@cross_origin()
#@token_required
def create_user():
    # if not current_user.admin:
    #     return jsonify({'message':'Cannot perform that function'})
    data = request.get_json(force=False, silent=False, cache=True)
    if(data["username"] == ""):
        return jsonify({'message':'username is invalid'}), 401

    if data['email'] == "":
        return jsonify({'message':'email is invalid'}), 401
    
    if ' ' in data['email'] :
        return jsonify({'message':'email is invalid'}), 401
    
    if(data["password"] == ""):
        return jsonify({'message':'passowrd is invalid'}), 401
    

    data['password'] = generate_password_hash(data['password'],'sha256')
    print(data['password'])
    data['user_id'] = str(uuid.uuid4())
    data['role'] = "User"
    data['admin'] = bool(True)
    
    try:
        new_user = User(data['user_id'], data['username'], data['email'], data['password'], data['role'], data['admin'])
        db.session.add(new_user)
        db.session.commit()
    except:
        return jsonify({'message' : 'This email is already taken'})

    return user_schema.jsonify(data)

#Login restful api
#Get all users infor
@auth.route('/user', methods=['GET'])
@cross_origin()
@token_required
def get_all_user(current_user, token):
    id = current_user.user_id
    print(id)
    if not current_user.admin:
        return jsonify({'message':'Cannot perform that function'})
    users = User.query.all()
    output=[]
    for user in users:
        user_data = {}
        user_data['user_id'] = user.user_id
        user_data['email'] = user.email
        user_data['username'] = user.username
        
        user_data['password'] = user.password
        user_data['role'] = user.role
        user_data['admin'] = user.admin
        output.append(user_data)
    return jsonify({'users':output})

#Get user information
@auth.route('/a_user', methods=['GET'])
@cross_origin()
@token_required
def get_a_user(current_user,token):
    user_id = current_user.user_id
    user = User.query.filter_by(user_id = user_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})

    user_data = {}
    user_data['user_id'] = user.user_id
    user_data['email'] = user.email
    user_data['username'] = user.username
    
    user_data['password'] = user.password
    user_data['role'] = user.role
    user_data['admin'] = user.admin
    return jsonify({'user': user_data})

#Edit user information
@auth.route('/user/<user_id>', methods=['PUT'])
@cross_origin()
@token_required
def edit_user(current_user, token,user_id):
    data = request.get_json()
    user = User.query.filter_by(user_id = user_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    if data.get('username'):
        user.firstname = data['username']
    
    if data.get('role'):
        user.role = data['role']
    #user.admin = True
    db.session.commit()
    return jsonify({'message' : 'The user has been edited'})

#Change password
@auth.route('/user/change_pass/<user_id>', methods = ['PUT'])
@cross_origin()
@token_required
def change_password(current_user, token, user_id):
    data = request.get_json()
    user = User.query.filter_by(user_id = user_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    
    if check_password_hash(user.password, data['old_password']):
        if data.get('new_password'):
            user.password = generate_password_hash(data['new_password'], 'sha256')
            db.session.commit()
            return jsonify({'message' : 'Password has changed'})

    print(check_password_hash(user.password, data['old_password']))
    return jsonify({'message' : 'Change password failed'})

#Delete User
@auth.route('/user/<user_id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_user(current_user,token, user_id):
    if not current_user.admin:
        return jsonify({'message':'Cannot perform that function'})
    user = User.query.filter_by(user_id = user_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message' : 'The user has been deleted'})

#Login user to generate token
@auth.route('/login', methods=['GET'])
@cross_origin()
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        
        return make_response('No fill', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(email=auth.username).first()


    if not user:
        return make_response('Not found user', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    
    #Sử dụng basic auth
    if check_password_hash(user.password, auth.password):
        #Tạo token theo user id + time now utc + duration (2000 phút) + secret key
        #Token sẽ tự động invalid khi hết 2000 phút
        token = jwt.encode({'public_id': user.user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=2000)}, app.config['SECRET_KEY'])
        print(token)
        return jsonify({'token' : token})
    
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

#Logout user and add to black list token
@auth.route('/logout', methods=['GET'])
@cross_origin()
@token_required
def logout(current_user, token):
    if current_user and token:
        #Add current token to black list table
        token_black_list = Token(user_id = current_user.user_id, token = token)
        db.session.add(token_black_list)
        db.session.commit()
        return jsonify({'message': 'The user has been loged out'})
    
    return jsonify({'message': 'Fail to logout'})

@auth.route('/verify-token', methods=['GET'])
@cross_origin()
@token_required
def verify_token(current_user, token):
    return jsonify({'message': True})
