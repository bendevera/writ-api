from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from functools import wraps

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
        # auth_header = request.headers.get('Authorization')
        # if request.method == "POST":
        #     auth_header = request.get_json()['token']
        # else:
        #     auth_header = request.args.get('token')
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
            'data': [work.to_json() for work in user.works]
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
        print("POST TO VERSIONS")
        work = Work.query.filter_by(user_id=request.user_id, id=work_id).first()
        new_version = work.new_version()
        responseObject = {
            'status': 'success',
            'data': new_version.to_json()
        }
        return make_response(jsonify(responseObject)), 200


class VersionAPI(MethodView):
    '''
    Version API
    /works/<work_id>/versions/<version_num>
    GET - Gets Version with number == version_num
    POST - Updates Version with number == version_num with JSON in request
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
        return make_response(jsonify(responseObject)), 401
    
    @login_required
    def post(self, work_id, version_num):
        version = Version.query.filter_by(work_id=work_id, number=version_num).first()
        if version is not None:
            payload = request.get_json()
            try:
                # DO I SEND THE WORK TITLE EACH TIME OR CREATE 
                # NEW UPDATE ROUTE FOR WORK TO CHANGE TITLE?
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
    methods=['GET', 'POST']
)
work_blueprint.add_url_rule(
    '/works/<work_id>/versions/<version_num>',
    view_func=version_view,
    methods=['GET', 'POST']
)
# @work_blueprint.route('/', methods=["GET"])
# @login_required
# def get_works():
#     '''
#     /works
#     GET - Returns ALL Works of the User.
#     '''
#     user = User.query.filter_by(id=request.user_id).first()
#     responseObject = {
#         'status': 'success',
#         'data': [work.to_json() for work in user.works]
#     }
#     return make_response(jsonify(responseObject)), 200


# @work_blueprint.route('/', methods=["POST"])
# @login_required
# def make_work():
#     '''
#     /works
#     POST - Creates a Work and returns it.
#     '''
#     new_work = Work(user_id=request.user_id)
#     db.session.add(new_work)
#     db.session.commit()
#     responseObject = {
#         'status': 'success',
#         'data': new_work.to_json()
#     }
#     return make_response(jsonify(responseObject)), 200


# @work_blueprint.route('/works/<work_id>')
# @login_required 
# def work_by_id(work_id):
#     '''
#     /works/<work_id>
#     GET - Returns Work with id == work_id
#     '''
#     work = Work.query.filter_by(user_id=request.user_id, id=work_id).first()
#     if work is None:
#         responseObject = {
#             'status': 'fail',
#             'message': 'provide a valid work id'
#         }
#         return make_response(jsonify(responseObject)), 401
#     responseObject = {
#         'status': 'success',
#         'data': work.to_json()
#     }
#     return make_response(jsonify(responseObject)), 200


# @work_blueprint.route('/works/<work_id>/versions', methods=["GET", "POST"])
# @login_required
# def versions_by_work__id(work_id):
#     '''
#     /works/<work_id>/versions
#     GET - Gets Versions of Work with id == work_id
#     POST - Creates a Version of the Work with a id == work_id
#     '''
#     work = Work.query.filter_by(user_id=request.user_id, id=work_id).first()
#     if request.method == "GET":
#         responseObject = {
#             'status': 'success',
#             'data': [version.to_json() for version in work.versions]
#         }
#         return make_response(jsonify(responseObject)), 200
#     elif request.method == "POST":
#         new_version = work.new_version()
#         responseObject = {
#             'status': 'success',
#             'data': new_version.to_json()
#         }
#         return make_response(jsonify(responseObject)), 200


# @work_blueprint.route('/works/<work_id>/versions/<version_num>', methods=["GET", "POST"])
# @login_required
# def version_by_id(work_id, version_num):
#     '''
#     /works/<work_id/versions/<version_num>
#     GET - Gets Version with number == version_num
#     POST - Updates Version with number == version_num with JSON in request
#     '''
#     version = Version.query.filter_by(work_id=work_id, number=version_num).first()
#     if version is not None:
#         if request.method == "GET":
#             responseObject = {
#                 'status': 'success',
#                 'data': version.to_json()
#             }
#             return make_response(jsonify(responseObject)), 200
#         elif request.method == "POST":
#             payload = request.get_json()
#             try:
#                 data = {
#                     "title": str(payload['title']),
#                     "text": str(payload['text'])
#                 }
#                 version.data = data
#                 db.session.commit()
#                 responseObject = {
#                     'status': 'success',
#                     'data': version.to_json()
#                 }
#                 return make_response(jsonify(responseObject)), 200
#             except:
#                 pass
#     responseObject = {
#         'status': 'fail',
#         'data': 'No version with number: {}'.format(version_num)
#     }
#     return make_response(jsonify(responseObject)), 401


@work_blueprint.route('/works/<work_id>/versions/<version_num>/collapse', methods=["POST"])
@login_required
def collapse_versions(work_id, version_num):
    '''
    /works/<work_id/versions/collapse/<version_num>
    POST - Collapses Version where number == version_num and returns all other versions
    '''
    try:
        work = Work.query.filter_by(user_id=request.user_id, id=work_id).first()
        new_versions = work.collapse(version_num)
        responseObject = {
            'status': 'success',
            'data': [version.to_json() for version in new_versions]
        }
        return make_response(jsonify(responseObject)), 200
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail',
            'data': 'Malformed collapse request.'
        }
        return make_response(jsonify(responseObject)), 401
