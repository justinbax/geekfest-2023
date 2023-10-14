import datetime as dt
from flask import Flask, jsonify, request
import requests
import json
import jwt

app = Flask(__name__)

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

def decode_token(jwtoken):
    # Querying Microsoft for URL to their signing keys
    url = "https://login.microsoftonline.com/4ea43e8a-132e-48c0-901d-52dd22e7cdf3/v2.0/.well-known/openid-configuration"
    ms_signingkey_response = requests.get(url)
    if ms_signingkey_response.status_code == 200:
        ms_signingkey_json = ms_signingkey_response.content
        ms_signingkey_url = json.loads(ms_signingkey_json)['jwks_uri']

        jwks_client = jwt.PyJWKClient(ms_signingkey_url)
        signing_key = jwks_client.get_signing_key_from_jwt(jwtoken)
        return jwt.decode(jwtoken, signing_key.key, algorithms=["RS256"])
    return None

def get_unique_name(jwtoken):
    token_content = decode_token(jwtoken)
    # TODO maybe use field 'sub' to uniquely identify users
    return token_content['email']

# TODO I don't think this is going to be in the final API
@app.route('/permissions')
def get_permissions():
    return jsonify(permissions)

@app.route('/user')
def get_user_data():
    return None

# Template response JSON
# {
#   'status': "GRANTED" or "DENIED" or "INVALID",
# }

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