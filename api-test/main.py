from enum import Enum
import datetime as dt
from flask import Flask, jsonify, request
import requests
import json
import jwt

app = Flask(__name__)

class PermissionStatus(Enum):
    PENDING = 0
    GRANTED = 1
    DENIED = 2

class User:
    def __init__(self, jwtoken, persistent_perms, supervisors, can_recieve_requests=True, co_supervisors=[]):
        token_content = decode_token(jwtoken)
        # TODO maybe use field 'sub' as uid
        self.uid = token_content['email']
        self.first_name = token_content['given_name']
        self.last_name = token_content['family_name']
        self.persistent_perms = persistent_perms
        self.active_perms = []
        self.denied_perms = []
        self.supervisors = supervisors
        self.co_supervisors = co_supervisors
        self.sent_requests = []
        self.recieved_requests = []
        self.has_co_supervisors = len(co_supervisors) > 0
        self.can_recieve_requests = can_recieve_requests

class Permission:
    def __init__(self, name, resource, holder, expiry_time, is_inherent=False):
        self.name
        self.resource = resource
        self.holder = holder
        self.expiry_time = expiry_time
        self.approved_time = get_current_time()
        self.is_inherent = is_inherent

class PermissionRequest:
    next_id = 0

    def __init__(self, resource_description, reason, duration, ip):
        self.id = PermissionRequest.next_id
        PermissionRequest.next_id += 1
        self.resource_description = resource_description
        self.time_sent = get_current_time()
        self.reason = reason
        self.duration = duration
        self.ip = ip
        self.status = PermissionStatus.PENDING

def get_current_time():
    # TODO this
    return 0

def decode_token(jwtoken):
    # TODO this
    result = {
        'email': 'arch@btw.com',
        'given_name': 'joe',
        'family_name': 'mama'
    }
    return result

@app.route('/show', methods=['GET'])
def get_user_data():
    # TODO this
    return

@app.route('/show', methods=['POST'])
def review_request():
    # TODO this
    return

@app.route('/check', methods=['GET'])
def check_permission():
    # TODO this
    return

@app.route('/request', methods=['POST'])
def receive_requests():
    # Identify permission level required to get file
    jwtoken = request.args.get('jwt')
    resource = request.args.get('resource')

    unique_name = get_unique_name(jwtoken)

    if unique_name in users:
        perms = users[unique_name]
    else:
        return jsonify({'status': 'INVALID'})

    response = {
        'status': 'DENIED'
    }
    # Verifies permission level
    if resource in permissions[perms]:
        response['status'] = 'GRANTED'

    return jsonify(response)