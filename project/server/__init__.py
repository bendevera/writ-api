# project/server/__init__.py

import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app.config.from_object(app_settings)
app.config['STATIC_FOLDER'] = 'build'

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# from project.server.react.views import react_blueprint
# app.register_blueprint(react_blueprint)
from project.server.auth.views import auth_blueprint
app.register_blueprint(auth_blueprint)
from project.server.work.views import work_blueprint
app.register_blueprint(work_blueprint)
# import project.server.frontend