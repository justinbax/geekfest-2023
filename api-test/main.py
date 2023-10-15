from enum import Enum
import time
from flask import Flask, jsonify, request
import requests
import json
import jwt

app = Flask(__name__)


class PermissionStatus(Enum):
    PENDING = 0
    GRANTED = 1
    DENIED = 2


def get_current_time():
    # TODO this
    return int(time.time())


def decode_token(jwtoken):
    # TODO this
    result = {
        'email': 'arch@btw.com',
        'given_name': 'joe',
        'family_name': 'mama'
    }
    return result


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


class User:
    def __init__(self, jwtoken, persistent_perms, requestable_resources, supervisors, can_receive_requests=True,
                 co_supervisors=[]):
        token_content = decode_token(jwtoken)
        # TODO maybe use field 'sub' as uid
        self.uid = token_content['email']
        self.first_name = token_content['given_name']
        self.last_name = token_content['family_name']
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


class Permission:
    def __init__(self, name, resource, holder, expiry_time, is_inherent=False):
        self.name = name
        self.resource = resource
        self.holder = holder
        self.expiry_time = expiry_time
        self.approved_time = get_current_time()
        self.is_inherent = is_inherent


class PermissionRequest:
    next_id = 0

    def __init__(self, resource, reason, duration, ip):
        self.id = PermissionRequest.next_id
        PermissionRequest.next_id += 1
        self.resource = resource
        self.time_sent = get_current_time()
        self.reason = reason
        self.duration = duration
        self.ip = ip
        self.status = PermissionStatus.PENDING


# TODO create actual users
users = [User('test', [], [], [])]


@app.route('/show', methods=['GET', ])
def get_user_data():
    # TODO this

    # Get JWT authentification from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)
    user = user_from_uid(token_contents['email'])

    return jsonify({'user': user.__dict__})


@app.route('/review', methods=['POST'])
def review_request():
    # TODO this
    return


@app.route('/check', methods=['GET'])
def check_permission():
    # Get JWT authentification from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)

    user = user_from_uid(token_contents['email'])

    resource = request.args.get('resource')

    if resource in user.active_perms:
        return "ACTIVE" + Permission  # OK
    else:
        return "DENIED", 403  # Forbidden


@app.route('/request', methods=['POST'])
def receive_requests():
    # Get JWT authentification from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)

    user = user_from_uid(token_contents['email'])

    resource = request.args['resource']
    reason = request.args['reason']
    duration = request.args['duration']
    # TODO get ip
    ip = '0.0.0.0'

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
    perm_request = PermissionRequest(resource, reason, duration, ip)
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
