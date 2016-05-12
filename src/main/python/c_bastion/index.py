from gevent import monkey; monkey.patch_all()

import os
import re
from os.path import normpath
from oidc import username_from_request, init_auth_url

import sh
from bottle import get, post, request, response, run

from . import __version__

REGEX_USERNAME = re.compile('^[a-z0-9_]+$')
HOME_PATH_PREFIX = '/home'
LIST_DISABLED_USERS = ['root']


class UsernameException(Exception):
    pass


@post('/delete')
def delete_user_entry_point():
    return delete_user()


@post('/create')
def create_user_entry_point():
    return create_user_with_key()


@get('/status')
def status():
    return 'OK'


@get('/version')
def version():
    return {'version': __version__}


def chown(path, username):
    sh.chown('-R', '{username}:{username}'.format(username=username), path)


def get_authorized_keys_path(username, home_dir):
    dir_ssh = os.path.join(home_dir, '.ssh')
    if not os.path.exists(dir_ssh):
        os.makedirs(dir_ssh, mode=0o700)
        chown(dir_ssh, username)
    return os.path.join(dir_ssh, 'authorized_keys')


def store_pubkey(username, home_dir, pubkey):
    auth_key_path = get_authorized_keys_path(username, home_dir)
    pubkey = '{0}\n'.format(pubkey.strip())
    file_descriptor = os.open(auth_key_path, os.O_WRONLY | os.O_CREAT, 0o600)
    with os.fdopen(file_descriptor, 'w') as file_pointer:
        file_pointer.write(pubkey)
    chown(home_dir, username)


def username_valid(username):
    return not (REGEX_USERNAME.search(username) is None or
                username in LIST_DISABLED_USERS)


def username_exists(username):
    try:
        sh.id(username)
    except sh.ErrorReturnCode_1:
        return False
    else:
        return True


def useradd(username):
    sh.useradd(username, '-b', HOME_PATH_PREFIX, '-p', '*', '-s', '/bin/bash')


def check_and_add(username):
    if not username_exists(username):
        useradd(username)
        return True
    else:
        return False


def create_user_with_key():
    """
    Create a user directory with a keyfile on the shared volume, data
    arriving in the payload of the request with a JSON payload.
    """
    username = username_from_request(request)
    if not username:
        response.status = 422
        return {'error': "Parameter 'username' not specified"}
    elif not username_valid(username):
        response.status = 400
        return {'error':
                "Invalid parameter 'username': '{0}' not allowed.".
                format(username)
                }

    pubkey = request.json.get('pubkey')
    if not pubkey:
        response.status = 422
        return {'error': "Parameter 'pubkey' not specified"}

    abs_home_path = normpath(os.path.join(HOME_PATH_PREFIX, username))

    username_was_added = check_and_add(username)

    # Do the actual creation
    store_pubkey(username, abs_home_path, pubkey)

    response.status = 201
    return {'response':
            'Successful creation of user {0} and/or upload of key.'
            .format(username)}


def check_and_delete(username):
    """
    Check if the user exists before killing his processes and deleting him.
    Raise UsernameException when user doesn't exist.
    """
    try:
        sh.id(username)
    except sh.ErrorReturnCode:
        raise UsernameException(
            400, {'error': 'Username {0} does not exist.'.format(username)})

    # User exists, kill him
    try:
        sh.pkill('-u', username, '-9')
    except sh.ErrorReturnCode:
        pass
    sh.userdel('-r', username)


def delete_user():
    username = username_from_request(request)

    if not username:
        response.status = 403
        return {'error': 'Permission denied'}

    try:
        check_and_delete(username)
    except UsernameException as exc:
        response.status = exc.args[0]
        return exc.args[1]

    response.status = 200
    return {'response': 'Successful deletion of user {0}.'.format(username)}


def run_server():
    init_auth_url()
    run(host='0.0.0.0', reloader=True, server="gevent")

