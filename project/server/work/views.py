from flask import Blueprint, request, make_response, jsonify
from functools import wraps

from project.server import bcrypt, db
from project.server.models import User, Work, Version, BlacklistToken

work_blueprint = Blueprint('work', __name__, url_prefix='/works')

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # user = User.query.filter_by(id=resp).first()
                # REPLACE responseObject.data with user.works
                # responseObject = {
                #     'status': 'success',
                #     'data': {
                #         'user_id': user.id,
                #         'email': user.email,
                #         'admin': user.admin,
                #         'registered_on': user.registered_on
                #     }
                # }
                request.user_id = resp
                return f(*args, **kwargs)
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401
    
    return wrap


@work_blueprint.route('/', methods=["GET", "POST"])
@login_required
def work_index():
    if request.method == "GET":
        user = User.query.filter_by(id=request.user_id).first()
        responseObject = {
            'status': 'success',
            'data': user.works
        }
        return make_response(jsonify(responseObject)), 200
    else:
        new_work = Work(user_id=request.user_id)
        db.session.add(new_work)
        db.session.commit()
        responseObject = {
            'status': 'success',
            'data': new_work.to_json()
        }
        return make_response(jsonify(responseObject)), 200


@work_blueprint.route('/<id>')
@login_required 
def work_by_id(id):
    work = Work.query.filter_by(user_id=request.user_id, id=id).first()
    if work is None:
        responseObject = {
            'status': 'fail',
            'message': 'provide a valid work id'
        }
        return make_response(jsonify(responseObject)), 401
    responseObject = {
        'status': 'success',
        'data': work.to_json()
    }
    return make_response(jsonify(responseObject)), 200