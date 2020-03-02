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


# @app.route("/site-map")
# def site_map():
#     links = []
#     for rule in app.url_map.iter_rules():
#         # Filter out rules we can't navigate to in a browser
#         # and rules that require parameters
#         if "GET" in rule.methods and has_no_empty_params(rule):
#             url = url_for(rule.endpoint, **(rule.defaults or {}))
#             links.append((url, rule.endpoint))
#     # links is now a list of url, endpoint tuples