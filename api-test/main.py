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

permissions = {
    'lvl0': ['/balls.txt', '/btw.txt'],
    'lvl1': ['/btw.txt'],
    'lvl2': []
}

users = {
    'joe@mama.com': 'lvl0',
    'mama@joe.com': 'lvl1',
    'chris@btw.com': 'lvl2'
}

def get_current_time():
    # TODO this
    return 0

def decode_token(jwtoken):
    # Querying Microsoft for URL to their signing keys
    url = "https://login.microsoftonline.com/4ea43e8a-132e-48c0-901d-52dd22e7cdf3/v2.0/.well-known/openid-configuration"
    signingkey_response = requests.get(url)

    try:
        signingkey = signingkey_response.content
        signingkey_url = json.loads(signingkey_json)['jwks_uri']

        jwks_client = jwt.PyJWKClient(signingkey_url)
        signing_key = jwks_client.get_signing_key_from_jwt(jwtoken)
        return jwt.decode(jwtoken, signing_key.key, algorithms=["RS256"])
    except:
        # TODO better handling
        print("Token decoding failed")
        return None

# TODO I don't think this is going to be in the final API
@app.route('/permissions')
def get_permissions():
    return jsonify(permissions)

@app.route('/user')
def get_user_data():
    return None

@app.route('/requests', methods=['GET'])
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