from flask import Blueprint, request, make_response, jsonify, send_from_directory
import os

react_blueprint = Blueprint('react', __name__, url_prefix="/", static_folder="build")


# Serve React App
@react_blueprint.route('/', defaults={'path': ''})
@react_blueprint.route('/<path:path>')
def serve(path):
    print(react_blueprint.static_folder + '/' + path)
    if path != "" and os.path.exists(react_blueprint.static_folder + '/' + path):
        return send_from_directory(react_blueprint.static_folder, path)
    else:
        return send_from_directory(react_blueprint.static_folder, 'index.html')