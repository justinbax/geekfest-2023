from enum import Enum
import time
from datetime import datetime
from flask import Flask, jsonify, request, Response
import requests
import json
import jwt
import authValidate
from flask_cors import CORS
import openai

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

users = []

openai.api_key = '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'

class PermissionStatus(Enum):
    PENDING = 0
    GRANTED = 1
    DENIED = 2


def get_current_time():
    return int(time.time())


def get_location(ip):
    response = requests.get(f'https://ipapi.co/{ip}/json/').json()
    location_data = {
        "ip": ip,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    print(location_data)
    return location_data


def decode_token(jwtoken):
    return authValidate.validate_auth_token(jwtoken)


def user_from_token(jwtoken):
    for u in users:
        if u.uid == jwtoken.get('email'):
            return u

    uid = jwtoken.get('email')
    persistent_perms = []
    requestable_resources = []
    supervisors_uid = []
    # This is a proof-of-concept to ensure everything works, user customization is still a thing to do
    if uid == 'chrisyx511@outlook.com':
        persistent_perms.append(Permission('Access level 1', 'file1.txt', get_current_time(), True))
        requestable_resources.append('reports/confidential.pdf')

    new_user = User(uid, jwtoken.get('given_name'), jwtoken.get('family_name'), persistent_perms, requestable_resources, supervisors_uid)

    users.append(new_user)
    log.log("User", f"Created user {new_user.first_name} {new_user.last_name} <{new_user.uid}>")
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

def query_openai(prompt, model='gpt-3.5-turbo'):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )

    return response.choices[0].message["content"]

def update_active_perms(active_perms):
    now = get_current_time()
    for act in active_perms:
        if act.expiry < now:
            active_perms.remove(act)

class User:
    def __init__(self, uid, first_name, last_name, persistent_perms, requestable_resources, supervisors_uid, can_receive_requests=True, co_supervisors_uid=[]):
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name
        self.persistent_perms = persistent_perms
        self.active_perms = []
        self.denied_perms = []
        self.requestable_resources = requestable_resources
        self.supervisors_uid = supervisors_uid
        self.co_supervisors_uid = co_supervisors_uid
        self.sent_requests = []
        self.received_requests = []
        self.has_co_supervisors = len(co_supervisors_uid) > 0
        self.can_receive_requests = can_receive_requests
    
    def serialize(self):
        return {
            'uid': self.uid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'persistent_perms': [p.serialize() for p in self.persistent_perms],
            'active_perms': [a.serialize() for a in self.active_perms],
            'denied_perms': [d.serialize() for d in self.denied_perms],
            'requestable_resources': self.requestable_resources,
            'supervisors_uid': self.supervisors_uid,
            'co_supervisors_uid': self.co_supervisors_uid,
            'sent_requests': [s.serialize() for s in self.sent_requests],
            'received_requests': [r.serialize() for r in self.received_requests],
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
        return self.__dict__

class PermissionRequest:
    next_id = 0

    def __init__(self, requester_uid, resource, reason, duration, ip, analysis):
        self.id = PermissionRequest.next_id
        PermissionRequest.next_id += 1
        self.requester_uid = requester_uid
        self.resource = resource
        self.time_sent = get_current_time()
        self.reason = reason
        self.duration = duration
        self.ip = ip
        self.analysis = analysis
        
    def serialize(self):
        return self.__dict__


class Log:
    def __init__(self, enabled, file_name):
        self.enabled = enabled
        self.log_file = None

        if enabled == True:
            self.log_file = open(file_name, 'a')
            self.log("Start", "Starting logging")

    def __del__(self):
        if self.enabled:
            self.log("Exit", "Exiting logging")
        close(self.log_file)
        
    def log(self, type, message):
        if self.enabled:
            time = datetime.now().strftime("[%Y/%m/%d %H:%M:%S]")
            self.log_file.write(f'{time} {type}: {message}\n')


log = Log(True, 'log.txt')


@app.route('/show', methods=['GET'])
def get_user_data():
    # Get JWT auethentication from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)
    if token_contents == False:
        return Response(jsonify({'error': 'Invalid JWT signature'}), status=403)

    user = user_from_token(token_contents)

    update_active_perms(user.active_perms)

    print("LOGGING")
    log.log("Show", f"/show request from {user.first_name} {user.last_name} <{user.uid}>")
    return jsonify({'user': user.serialize()})


@app.route('/review', methods=['POST'])
def review_request():
    # Get JWT authentication from HTTP header
    # TODO auto refuse is supervisor doesn't have access
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)
    
    if token_contents == False:
        return Response(jsonify({'error': 'Invalid JWT signature'}), status=403)

    user = user_from_token(token_contents)

    post_data = request.get_json()

    if not ('id' in post_data and 'status' in post_data and 'expiry' in post_data):
        return Response(jsonify({'error': 'Invalid JSON input'}), status=403)

    request_id = post_data['id']
    status = post_data['status']
    expiry_mins = post_data['expiry']

    expiry = get_current_time() + expiry_mins

    request_reviewed = search_requests_for_id(user.received_requests, request_id)
    if request_reviewed == None:
        return Response(jsonify({'error': 'Invalid request id'}), status=403)

    if not(request_reviewed in user.received_requests and request_reviewed in request_reviewed.requester.sent_request):
        log.log("Error", f"Failed to remove request id {request_id} from received or sent requests in /review")
        return Response(jsonify({"error": "Couldn't find request id"}), status=403)

    user.received_requests.remove(request_reviewed)
    request_reviewed.requester.sent_requests.remove(request_reviewed)

    new_permission = Permission(f'Access to {request_reviewed.resource}', request_reviewed.resource, request_reviewed.requester, expiry)
    if status == 'GRANTED':
        log.log("Review", f"Permission request id {request_reviewed.id} to {request_reviewed.resource} granted from {user.first_name} {user.last_name} <{user.uid}>")
        request_reviewed.requester.active_perms.append(new_permission)
    else:
        # TODO what do we do with that?
        log.log("Review", f"Permission request id {request_reviewed.id} to {request_reviewed.resource} denied from {user.first_name} {user.last_name} <{user.uid}>")
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

    if not 'resource' in request.args:
        return Response(jsonify({'error': 'Invalid JSON input'}), status=403)
    resource = request.args.get('resource')

    update_active_perms(user.active_perms)

    if (result := search_permissions_for_resource(user.active_perms, resource) != None):
        return jsonify({
            'status': 'ACTIVE',
            'permission': result.serialize()
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

    if not ('resource' in post_data and 'reason' in post_data and 'duration' in post_data):
        return Response(jsonify({'error': 'Invalid JSON input'}), status=403)

    resource = post_data['resource']
    reason = post_data['reason']
    duration = post_data['duration']
    ip = request.remote_addr
    location = get_location(ip)

    update_active_perms(user.active_perms)

    if (result := search_permissions_for_resource(user.active_perms, resource)) != None:
        return jsonify({
            'status': 'ACTIVE',
            'permission': result.serialize()
        })

    if (result := search_permissions_for_resource(user.persistent_perms, resource)) != None:
        log.log("Request", f"Request automatically granted for {resource} for user {user.first_name} {user.last_name} <{user.uid}> because in persistent perms.")
        return jsonify({
            'status': 'GRANTED',
            'permission': result.serialize()
        })

    if (result := search_permissions_for_resource(user.denied_perms, resource)) != None:
        log.log("Request", f"Request automatically denied for {resource} for user {user.first_name} {user.last_name} <{user.uid}> because in denied perms.")
        return jsonify({
            'status': 'DENIED',
            'permission': result.serialize()
        })

    # TODO right now we don't check if resource is in requestable_resources because, with the UI, it should always be. but probably better idea to check
    perm_request = PermissionRequest(user, resource, reason, duration, ip)
    user.sent_requests.append(perm_request)

    # TODO machine learning and heuristic stuff
    analysis = ""
    if location['city'] != 'Montreal':
        analysis.append(f"Warning: IP address originates from outside Montreal (city: {location['city']})\n")

    gpt_prompt = f"We received a request to access a resource that may contain personal information named: '{resource}'.\
        I need you to help us determine if the request is from a valid source r if it may be used for malicious intent.\
        The requester provided a reason to access the data, here it is: '{reason}'.\
        Considering the reason and the name of the resource, can you help us analyze if this request is legit? Provide a very short analysis of 10 to 20 words."

    gpt_response = query_openai(gpt_prompt)
    print(gpt_response)

    if len(user.supervisors_uid) != 0:
        # Ask supervisors
        for sup_uid in user.supervisors_uid:
            sup = user_from_uid(sup_uid)
            if sup != None:
                sup.received_requests.append(perm_request)
            else:
                log.log("Error", f"Couln't find supervisor from uid <{sup_uid}> for user {user.first_name} {user.last_name} <{user.uid}>")
    else:
        # Ask co-supervisors
        for co_uid in user.co_supervisors_uid:
            co = user_from_uid(co_uid)
            if co != None:
                co.received_requests.append(perm_request)
            else:
                log.log("Error", f"Couldn't find co-supervisor from uid <{co_uid}> for user {user.first_name} {user.last_name} <{user.uid}>")

    log.log("Request", f"Received pending request for {resource} from {user.first_name} {user.last_name} <{user.uid}>")
    return jsonify({
        'status': 'PENDING',
    })