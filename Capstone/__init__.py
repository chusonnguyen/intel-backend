from flask import Flask
from flask_mysqldb import MySQL
#import bootstrap: pip install flask_bootstrap
from flask_bootstrap import Bootstrap
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
UPLOAD_FOLDER = 'Capstone/upload_file'


def create_app():
    application =app= Flask(__name__)
    application.secret_key='14320edb76fb8c6018c28b07'
    cors = CORS(application)
    global ma
    global db
    ma=Marshmallow(application)
    #engine=create_engine('mysql://admin:password123''@flask2.cluster-ck2xdeldx037.us-west-2.rds.amazonaws.com/flask2')

    db=SQLAlchemy(application)
    #Secret key for privacy DON'T SHARE!
    application.config['CORS_HEADER'] = 'Content-Type'
    application.config['SECRET_KEY'] = '14320edb76fb8c6018c28b07'
    application.config['MYSQL_HOST'] = 'flask2.cluster-ck2xdeldx037.us-west-2.rds.amazonaws.com'
    application.config['MYSQL_USER'] = 'admin'
    application.config['MYSQL_PASSWORD'] = 'password123'
    application.config['MYSQL_DB'] = 'flask2'
    application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    global mysql
    mysql = MySQL(application)
    Bootstrap(application)

    from .views import views
    from .auth import auth
    from .project import project
    from .existedzone import existedzone
    from .refreshedzone import refreshedzone
    from .dashboard import dashboard
    from .layout import layout
    from .projecthistory import projecthistory
    from .zonehistory import zonehistory
    from .crates import crates
    from .zonestatistics import zonestatistics
    from .history import history
    from .playground import playground
    from .pole import pole
    from .ailse import ailse
    from .chart import chart
    
    application.register_blueprint(views,url_prefix='/')
    application.register_blueprint(auth,url_prefix='/')
    application.register_blueprint(project,url_prefix='/')
    application.register_blueprint(existedzone,url_prefix='/')
    application.register_blueprint(refreshedzone,url_prefix='/')
    application.register_blueprint(dashboard,url_prefix='/dashboard/')
    application.register_blueprint(layout,url_prefix='/layout/')
    application.register_blueprint(pole,url_prefix='/pole/')
    application.register_blueprint(ailse, url_prefix='/ailse/')
    application.register_blueprint(playground, url_prefix='/playground/')
    application.register_blueprint(projecthistory,url_prefix='/project/history/')
    application.register_blueprint(chart, url_prefix='/chart/')
    application.register_blueprint(history, url_prefix='/history/')
    application.register_blueprint(zonehistory,url_prefix='/zone/history/')
    application.register_blueprint(crates,url_prefix='/')
    application.register_blueprint(zonestatistics,url_prefix='/stats/')

    return application
