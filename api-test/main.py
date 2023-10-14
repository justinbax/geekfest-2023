import datetime as dt
from flask import Flask, jsonify, request

app = Flask(__name__)

permissions = ['Access to very important files', 'Access to authenticated files', 'Access to base files']


@app.route('/permissions')
def get_permissions():
    return jsonify(permissions)

@app.route('requests', methods=['POST'])
def receive_requests():
    return