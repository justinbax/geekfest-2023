from enum import Enum
import time
from flask import Flask, jsonify, request, Response
import requests
import json
import jwt
import authValidate
from flask_cors import CORS

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

users = []

class PermissionStatus(Enum):
    PENDING = 0
    GRANTED = 1
    DENIED = 2


def get_current_time():
    return int(time.time())

def get_location():
    return 0

def decode_token(jwtoken):
    return authValidate.validate_auth_token(jwtoken)


def user_from_token(jwtoken):
    for u in users:
        if u.uid == jwtoken.get('email'):
            return u
    
    new_user = User(jwtoken.get('email'), jwtoken.get('given_name'), jwtoken.get('family_name'), [], [], [])
    users.append(new_user)
    return new_user

def user_from_uid(uid):
    for u in users:
        if u.uid == uid:
            return u
        
    return None


def search_permissions_for_resource(permissions, resource):
    for perm in permissions:
        if perm.resource == resource:
            return perm
    return None

def search_requests_for_id(requests, req_id):
    for req in requests:
        if req.id == req_id:
            return req


class User:
    def __init__(self, uid, first_name, last_name, persistent_perms, requestable_resources, supervisors, can_receive_requests=True, co_supervisors=[]):
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name
        self.persistent_perms = persistent_perms
        self.active_perms = []
        self.denied_perms = []
        self.requestable_resources = requestable_resources
        self.supervisors = supervisors
        self.co_supervisors = co_supervisors
        self.sent_requests = []
        self.received_requests = []
        self.has_co_supervisors = len(co_supervisors) > 0
        self.can_receive_requests = can_receive_requests
    
    def serialize(self):
        return {
            'uid': self.uid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            #self.persistent_perms = persistent_perms
            #self.active_perms = []
            #self.denied_perms = []
            'requestable_resources': self.requestable_resources,
            #self.supervisors = supervisors
            #self.co_supervisors = co_supervisors
            #self.sent_requests = []
            #self.received_requests = []
            'has_co_supervisors': self.has_co_supervisors,
            'can_receive_requests': self.can_receive_requests
        }


class Permission:
    def __init__(self, name, resource, expiry_time, is_inherent=False):
        self.name = name
        self.resource = resource
        self.expiry_time = expiry_time
        self.approved_time = get_current_time()
        self.is_inherent = is_inherent
    
    def serialize(self):
    def serialize(self):
        return {
            'name': self.name,
            'resource': self.resource,
            # 'holder': self.holder.serialize,
            'expiry_time': self.expiry_time,
            'approved_time': self.approved_time,
            'is_inherent': self.is_inherent
        }

class PermissionRequest:
    next_id = 0

    def __init__(self, requester_uid, resource, reason, duration, ip):
        self.id = PermissionRequest.next_id
        PermissionRequest.next_id += 1
        self.requester_uid = request_uid
        self.resource = resource
        self.time_sent = get_current_time()
        self.reason = reason
        self.duration = duration
        self.ip = ip
        
    def serialize(self):
        return self.__dict__


@app.route('/show', methods=['GET'])
def get_user_data():
    # Get JWT auethentication from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)
    if token_contents == False:
        return Response(jsonify({'error': 'Invalid JWT signature'}), status=403)

    user = user_from_token(token_contents)

    return jsonify({'user': user.__dict__})


@app.route('/review', methods=['POST'])
def review_request():
    # Get JWT authentication from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)
    
    if token_contents == False:
        return Response(jsonify({'error': 'Invalid JWT signature'}), status=403)

    user = user_from_token(token_contents)

    post_data = request.get_json()

    request_id = post_data['id']
    status = post_data['status']
    expiry_mins = post_data['expiry']

    expiry = get_current_time() + expiry_mins

    # TODO Have actual error handling lmao
    request_reviewed = search_requests_for_id(user.received_requests, request_id)
    user.received_requests.remove(request_reviewed)

    request_reviewed.requester.sent_requests.remove(request_reviewed)

    # TODO generate name
    new_permission = Permission(request_reviewed.resource, request_reviewed.resource, request_reviewed.requester, expiry)
    if status == 'GRANTED':
        request_reviewed.requester.active_perms.append(new_permission)
    else:
        # TODO what do we do with that?
        new_permission.expiry_time = 0
        request_reviewed.requester.denied_perms.append(new_permission)

    return jsonify({
        'permission': request_reviewed.serialize()
    })

@app.route('/check', methods=['GET'])
def check_permission():
    # Get JWT authentication from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)

    if token_contents == False:
        return Response(jsonify({'error': 'Invalid JWT signature'}), status=403)

    user = user_from_token(token_contents)

    resource = request.args.get('resource')


    if (result := search_permissions_for_resource(user.active_perms, resource) != None):
        return jsonify({
            'status': 'ACTIVE',
            'permission': result
        })
    else:
        return jsonify({
            'status': 'DENIED'
        })


@app.route('/request', methods=['POST'])
def receive_requests():
    # Get JWT authentification from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)

    if token_contents == False:
        return Response(jsonify({'error': 'Invalid JWT signature'}), status=403)

    user = user_from_token(token_contents)
    post_data = request.get_json()

    resource = post_data['resource']
    reason = post_data['reason']
    duration = post_data['duration']
    # TODO get ip
    ip = '0.0.0.0'
    location = get_location()

    if (result := search_permissions_for_resource(user.active_perms, resource)) != None:
        return jsonify({
            'status': 'ACTIVE',
            'permission': result
        })

    if (result := search_permissions_for_resource(user.persistent_perms, resource)) != None:
        return jsonify({
            'status': 'GRANTED',
            'permission': result
        })

    if (result := search_permissions_for_resource(user.denied_perms, resource)) != None:
        return jsonify({
            'status': 'DENIED',
            'permission': result
        })

    # TODO right now we don't check if resource is in requestable_resources because, with the UI, it should always be. but probably better idea to check
    perm_request = PermissionRequest(user, resource, reason, duration, ip)
    user.sent_requests.append(perm_request)

    # TODO machine learning and heuristic stuff
    if len(user.supervisors) != 0:
        # Ask supervisors
        for sup in user.supervisors:
            sup.received_requests.append(perm_request)
    else:
        # Ask co-supervisors
        for co in user.co_supervisors:
            co.received_requests.append(perm_request)

    return jsonify({
        'status': 'PENDING',
    })