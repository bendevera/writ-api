# project/server/__init__.py
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from project.server.config import DevelopmentConfig, ProductionConfig


app = Flask(__name__)
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.ProductionConfig'
)
app.config.from_object(ProductionConfig)
app.config['STATIC_FOLDER'] = 'build'
print(app.config['SQLALCHEMY_DATABASE_URI'])

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# from project.server.react.views import react_blueprint
# app.register_blueprint(react_blueprint)
from project.server.auth.views import auth_blueprint
app.register_blueprint(auth_blueprint)
from project.server.work.views import work_blueprint
app.register_blueprint(work_blueprint)
# import project.server.frontend