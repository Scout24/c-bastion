#!/usr/bin/env python

import os
from bottle import Bottle, request, run
from calendar import timegm
from datetime import datetime

app = Bottle()

TOKEN = 'my-nifty-access-token'
AUTH_URL = "http://your-auth-server.test"
USER = 'integrationtestuser'


def init_auth_url():
    global AUTH_URL
    AUTH_URL = os.environ['AUTH_URL']


@app.get('/status')
def status():
    return 'OK'


@app.route('/oauth/token', method='POST')
def auth_server():
    username = request.forms.get('username')
    if username == USER:
        return {'access_token': TOKEN}


@app.route('/oauth/user_info', method='GET')
def create():
    auth_token = request.headers.get('Authorization').split()[1]
    if auth_token == TOKEN:
        now = timegm(datetime.utcnow().utctimetuple())
        return {'aud': 'jumpauth',
                'exp': now + 3600,
                'iat': now,
                'iss': AUTH_URL,
                'scope': ['any_scope'],
                'sub': USER,
                }

init_auth_url()
auth_port = os.environ.get('AUTH_PORT') or 8943
run(app, host='0.0.0.0', port=auth_port, debug=True, reloader=True)
