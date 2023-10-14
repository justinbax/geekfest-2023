import datetime as dt
from flask import Flask, jsonify, request
import requests

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

def get_unique_name(uuid):
    # TODO this
    return 'chris@btw.com'

@app.route('/permissions')
def get_permissions():
    return jsonify(permissions)

# Template response JSON
# {
#   'status': "GRANTED" or "DENIED",
# }

@app.route('/requests', methods=['GET'])
def receive_requests():
    # Identify permission level required to get file
    uuid = request.args.get('uuid')
    resource = request.args.get('resource')

    unique_name = get_unique_name(uuid)

    if unique_name in users:
        perms = users[unique_name]
    else:
        return jsonify({'status': 'INVALID'})

    response = {
        'status': 'DENIED'
    }
    # Verifies permission level
    if resource in permissions[perms]:
        # yay
        response['status'] = 'GRANTED'

    return jsonify(response)