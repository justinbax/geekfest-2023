from enum import Enum
import time
from flask import Flask, jsonify, request
import requests
import json
import jwt
import authValidate

app = Flask(__name__)


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

    def __init__(self, requester, resource, reason, duration, ip):
        self.id = PermissionRequest.next_id
        PermissionRequest.next_id += 1
        self.requester = requester
        self.resource = resource
        self.time_sent = get_current_time()
        self.reason = reason
        self.duration = duration
        self.ip = ip
        self.status = PermissionStatus.PENDING


# TODO create actual users
some_perms = [Permission('arch', 'something', None, 1234)]
users = [User('eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjlHbW55RlBraGMzaE91UjIybXZTdmduTG83WSIsImtpZCI6IjlHbW55RlBraGMzaE91UjIybXZTdmduTG83WSJ9.eyJhdWQiOiJhcGk6Ly84NGY2YzEyYS0xMmJmLTRmZDAtOTFiYy0yZGZiMzBlY2FkZWEiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC80ZWE0M2U4YS0xMzJlLTQ4YzAtOTAxZC01MmRkMjJlN2NkZjMvIiwiaWF0IjoxNjk3MzQ0ODIxLCJuYmYiOjE2OTczNDQ4MjEsImV4cCI6MTY5NzM0OTAwOSwiYWNyIjoiMSIsImFpbyI6IkFhUUFXLzhVQUFBQVlDRXRJZjlzK0oydEpSTWtuUXZ6UUJRRmpDUjQ4R1UyR2ZtaUZhTU8zU0xCaThWcGYvK2hnTmRNQitJVlFXK2tjZm5EL2R2OXJPRTBlMjlxV25HS2o1M1Nkb1h5MG9MYnYzWi9rZHhocWF0YloyeWdtZUtwSmFqUlV0ejdmb1B6b0thT3AwYlVJeWNJSEF3L2ZFV3VxRWFhSVVSenl5OUVmaWptM3hJT204RVFtS2EwOEU1WERXdU5ubS9WUXRWRXlIcVVqQng2U1lEQXlFakFndDBCelE9PSIsImFtciI6WyJwd2QiLCJtZmEiXSwiYXBwaWQiOiI4NGY2YzEyYS0xMmJmLTRmZDAtOTFiYy0yZGZiMzBlY2FkZWEiLCJhcHBpZGFjciI6IjAiLCJlbWFpbCI6ImNocmlzeXg1MTFAb3V0bG9vay5jb20iLCJmYW1pbHlfbmFtZSI6IllhbmciLCJnaXZlbl9uYW1lIjoiQ2hyaXMiLCJpZHAiOiJsaXZlLmNvbSIsImlwYWRkciI6IjY1LjM4LjcwLjIzOCIsIm5hbWUiOiJDaHJpcyBZYW5nIiwib2lkIjoiODExMDQ3MzUtMGIzYi00NTQzLTg2YzYtZmEwMDk2NTFjNjM3IiwicmgiOiIwLkFiMEFpajZrVGk0VHdFaVFIVkxkSXVmTjh5ckI5b1NfRXRCUGtid3QtekRzcmVxOUFNOC4iLCJzY3AiOiJBY2Nlc3NQZXJtcyIsInN1YiI6IlFFYTJsb1FVdmpXcTJyZFBVVldQeWtDUFNMX2F5OHBGMHk2ajdYdF85QUEiLCJ0aWQiOiI0ZWE0M2U4YS0xMzJlLTQ4YzAtOTAxZC01MmRkMjJlN2NkZjMiLCJ1bmlxdWVfbmFtZSI6ImxpdmUuY29tI2NocmlzeXg1MTFAb3V0bG9vay5jb20iLCJ1dGkiOiJKZU5ZdjRtczZFT0E4LWt3Y1pJYUFBIiwidmVyIjoiMS4wIn0.aBjyREERbQ2EdzsyOsAF59liEzWbgphI99DlTAYD3QPhJiWnq1TjnHeVyiVsgQzDVLwMD-lp7shvFi_OcTyaWeUt4AfZ2HaAh51PvCQFVYINXaJow2L-C6hLnmJQciraJAB0e9uZA5zHikQQQ3fHr50kw5_NkrCbp7TZoQLJa-sDP_FnqsXNcANH_EkgfE2joELjtqwaFDAb_5pldbcLQy0DAvzj9ZIJ7fgBFWD7ZxiUQ0MlWb2gxIoMJYI2DcoXMMzbpflSBB1xwW7uaLv_1ZKKip2ybYndUKG97g3zu34GTMtz9zLTRjgSWkWyoEBxJvv4Bq7yNA-fOW-TJAcXNA', [], [], [])]
users[0].active_perms = some_perms


@app.route('/show', methods=['GET'])
def get_user_data():
    # Get JWT authentification from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)

    user = user_from_uid(token_contents['email'])

    return jsonify({'user': user.__dict__})


@app.route('/review', methods=['POST'])
def review_request():
    # Get JWT authentification from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)

    user = user_from_uid(token_contents['email'])

    post_data = request.get_json()

    request_id = post_data['id']
    status = post_data['status']
    expiry_mins = post_data['expiry']

    expiry = get_current_time() + expiry_mins * 60

    # TODO Have actual error handling lmao
    request_reviewed = search_requests_for_id(user.received_requests, request_id)
    print(request_reviewed)
    print(user.received_requests[0])
    user.received_requests.remove(request_reviewed)

    request_reviewed.requester.sent_requests.remove(request_reviewed)

    # TODO generate name
    new_permission = Permission(resource, resource, request_reviewed.requester, expiry)
    if status == 'GRANTED':
        request_reviewed.requester.active_perms.append(new_permission)
    else:
        # TODO what do we do with that?
        new_permission.expiry_time = 0
        request_reviewed.requester.denied_perms.append(new_permission)

@app.route('/check', methods=['GET'])
def check_permission():
    # Get JWT authentification from HTTP header
    jwtoken = request.headers['Authorization']
    jwtoken = jwtoken.split()[1]
    token_contents = decode_token(jwtoken)

    user = user_from_uid(token_contents['email'])

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

    user = user_from_uid(token_contents['email'])

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

    # TODO REMOVE THIS REMOVE THIS REMOVE THIS
    # TODO REMOVE THIS REMOVE THIS REMOVE THIS
    # TODO REMOVE THIS REMOVE THIS REMOVE THIS
    user.received_requests.append(perm_request)
    # TODO REMOVE THIS REMOVE THIS REMOVE THIS
    # TODO REMOVE THIS REMOVE THIS REMOVE THIS
    # TODO REMOVE THIS REMOVE THIS REMOVE THIS
    # TODO REMOVE THIS REMOVE THIS REMOVE THIS
    # TODO REMOVE THIS REMOVE THIS REMOVE THIS

    return jsonify({
        'status': 'PENDING'
    })