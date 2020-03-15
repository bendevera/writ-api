from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from functools import wraps
import datetime

from project.server import bcrypt, db
from project.server.models import User, Work, Version, BlacklistToken
from flask_cors import cross_origin

work_blueprint = Blueprint('work', __name__)

def login_required(f):
    '''
    Ensures request includes a valid token before 
    proceeding with the request.
    '''
    @wraps(f)
    def wrap(*args, **kwargs):
        # token in header
        # auth_header = request.headers.get('Authorization')
        # token in json
        # auth_header = request.get_json()['token']
        # token in query string
        auth_header = request.args.get('token')
        if auth_header:
            try:
                # auth_token = auth_header.split(" ")[1]
                auth_token = auth_header.strip()
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

class WorksAPI(MethodView):
    """
    Works API
    /works
    GET - Returns ALL Works of the User.
    POST - Creates a Work and returns it.
    """

    @login_required
    def get(self):
        user = User.query.filter_by(id=request.user_id).first()
        responseObject = {
            'status': 'success',
            'data': [work.to_json() for work in sorted(user.works, key=lambda x: x.last_updated, reverse=True)]
        }
        return make_response(jsonify(responseObject)), 200

    @login_required
    def post(self):
        new_work = Work(user_id=request.user_id)
        db.session.add(new_work)
        db.session.commit()
        responseObject = {
            'status': 'success',
            'data': new_work.to_json()
        }
        return make_response(jsonify(responseObject)), 200


class VersionsAPI(MethodView):
    '''
    Versoins API
    /works/<work_id>/versions
    GET - Gets Versions of Work with id == work_id
    POST - Creates a Version of the Work with a id == work_id
    '''

    @login_required
    def get(self, work_id):
        print("GET TO VERSIONS")
        work = Work.query.filter_by(user_id=request.user_id, id=work_id).first()
        responseObject = {
            'status': 'success',
            'data': [version.to_json() for version in work.versions]
        }
        return make_response(jsonify(responseObject)), 200
    
    @login_required
    def post(self, work_id):
        payload = request.get_json()
        work = Work.query.filter_by(user_id=request.user_id, id=work_id).first()
        try:
            new_version = work.new_version(payload['number'])
            responseObject = {
                'status': 'success',
                'data': new_version.to_json()
            }
            return make_response(jsonify(responseObject)), 200
        except Exception as e:
            print("ERROR MAKING VERSION")
            print(e)
            responseObject = {
                'status': 'fail',
                'data': 'Failed attempt. Please try again.'
            }
            return make_response(jsonify(responseObject)), 404
    
    @login_required
    def delete(self, work_id):
        try:
            work = Work.query.filter_by(user_id=request.user_id, id=work_id).first()
            db.session.delete(work)
            db.session.commit()
            responseObject = {
                'status': 'success',
                'data': 'success'
            }
            return make_response(jsonify(responseObject)), 200
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'data': 'Malformed collapse request.'
            }
            return make_response(jsonify(responseObject)), 401



class VersionAPI(MethodView):
    '''
    Version API
    /works/<work_id>/versions/<version_num>
    GET - Gets Version with number == version_num
    POST - Updates Version with number == version_num with JSON in request
    DELETE - Deletes Version with number == version_num
    '''
    
    @login_required
    def get(self, work_id, version_num):
        version = Version.query.filter_by(work_id=work_id, number=version_num).first()
        if version is not None:
            responseObject = {
                'status': 'success',
                'data': version.to_json()
            }
            return make_response(jsonify(responseObject)), 200
        responseObject = {
            'status': 'fail',
            'data': 'No version with number: {}'.format(version_num)
        }
        return make_response(jsonify(responseObject)), 404
    
    @login_required
    def post(self, work_id, version_num):
        work = Work.query.filter_by(id=work_id).first()
        version = None
        for vers in work.versions:
            if vers.number == int(version_num):
                version = vers
        # version = Version.query.filter_by(work_id=work_id, number=version_num).first()
        if version is not None:
            payload = request.get_json()
            try:
                # DO I SEND THE WORK TITLE EACH TIME OR CREATE 
                # NEW UPDATE ROUTE FOR WORK TO CHANGE TITLE?
                work.title = str(payload['title'])
                work.last_updated = datetime.datetime.now()
                data = {
                    "text": str(payload['text'])
                }
                version.data = data
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'data': version.to_json()
                }
                return make_response(jsonify(responseObject)), 200
            except:
                pass
        responseObject = {
            'status': 'fail',
            'data': 'No version with number: {}'.format(version_num)
        }
        return make_response(jsonify(responseObject)), 404
    
    @login_required
    def delete(self, work_id, version_num):
        try:
            work = Work.query.filter_by(user_id=request.user_id, id=work_id).first()
            print(work.versions)
            work.collapse(int(version_num))
            print(work.versions)
            responseObject = {
                'status': 'success',
                'data': 'success'
            }
            return make_response(jsonify(responseObject)), 200
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'data': 'Malformed collapse request.'
            }
            return make_response(jsonify(responseObject)), 401

# define the APIs
works_view = WorksAPI.as_view('works_api')
versions_view = VersionsAPI.as_view('versions_api')
version_view = VersionAPI.as_view('version_api')

# add Rules for API Endpoints
work_blueprint.add_url_rule(
    '/works',
    view_func=works_view,
    methods=['GET', 'POST']
)
work_blueprint.add_url_rule(
    '/works/<work_id>/versions',
    view_func=versions_view,
    methods=['GET', 'POST', 'DELETE']
)
work_blueprint.add_url_rule(
    '/works/<work_id>/versions/<version_num>',
    view_func=version_view,
    methods=['GET', 'POST', 'DELETE']
)