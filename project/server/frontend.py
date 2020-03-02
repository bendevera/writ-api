# project/server/frontend.py
from project.server import app as APP
from flask import request, make_response, jsonify, send_from_directory
import os


# Serve React App
@APP.route('/', defaults={'path': ''})
@APP.route('/<path:path>')
def serve(path):
    print(APP.static_folder + '/' + path)
    if path != "" and os.path.exists(APP.static_folder + '/' + path):
        return send_from_directory(APP.static_folder, path)
    else:
        return send_from_directory(APP.static_folder, 'index.html')