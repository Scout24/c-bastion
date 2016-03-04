#!/usr/bin/env python

import os
from bottle import Bottle, request, run
from calendar import timegm
from datetime import datetime

app = Bottle()

TOKEN = 'my-nifty-access-token'
AUTH_URL = "http://your-auth-server.test"


def init_auth_url():
    global AUTH_URL
    AUTH_URL = os.environ['AUTH_URL']


@app.get('/status')
def status():
    return 'OK'


@app.route('/oauth/token', method='POST')
def auth_server():
    username = request.forms.get('username')
    if username == 'integration-test-user':
        return {'access_token': TOKEN}


@app.route('/oauth/user/info', method='GET')
def create():
    auth_token = request.headers.get('Authorization').split()[1]
    if auth_token == TOKEN:
        now = timegm(datetime.utcnow().utctimetuple())
        return {'aud': 'jumphost',
                'exp': now + 3600,
                'iat': now,
                'iss': AUTH_URL,
                'scope': ['any_scope'],
                'sub': 'integration-test-user',
                }

init_auth_url()
run(app, host='0.0.0.0', port=8943, debug=True, reloader=True)
