import os
import re
from os.path import normpath
from oidc import username_from_request

import sh
from bottle import get, post, request, response, run

REGEX_USERNAME = re.compile('^[a-z0-9_]+$')
PATH_PREFIX = '/data/home'
LIST_DISABLED_USERS = ['root']


class UsernameException(BaseException):
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


def store_pubkey(username, home_dir, pubkey):
    """
    Create the user's directory and copy the public key into it.
    Also, set the proper permissions.
    """
    dir_ssh = os.path.join(home_dir, '.ssh')
    if not os.path.exists(dir_ssh):
        os.makedirs(dir_ssh, mode=0o700)
    auth_key_path = os.path.join(dir_ssh, 'authorized_keys')
    pubkey = '{0}\n'.format(pubkey.strip())
    with open(auth_key_path, 'wb') as fd:
        fd.write(pubkey)
    os.chmod(auth_key_path, 0o600)
    sh.chown('-R', '{username}:{username}'.format(username=username), home_dir)


def check_username(username):
    """
    Check the format of the username against various rules.
    """
    if username is None:
        raise UsernameException(
            400, {
                'error': 'Parameter \'username\' not specified.'})
    if REGEX_USERNAME.search(username) is None:
        raise UsernameException(
            403, {
                'error': 'Invalid parameter \'username\': \'{0}\''.format(
                    username)})
    if username in LIST_DISABLED_USERS:
        raise UsernameException(
            404, {
                'error': 'Invalid parameter \'username\': \'{0}\' not '
                'allowed.'.format(username)})


def check_and_add(username):
    """
    Check if the user already exists.

    Raise UsernameException when it exists, create when not.
    """
    try:
        sh.id(username)
    except sh.ErrorReturnCode:
        if not os.path.exists(PATH_PREFIX):
            # If the initial homes don't exist, create them with the right mode
            os.makedirs(PATH_PREFIX, mode=0o755)
        # User does not exist, add it
        sh.useradd(
            username, '-b', PATH_PREFIX, '-p', '*', '-s', '/bin/bash')
        return
    raise UsernameException(
        400, {'error': 'Username {0} already exists.'.format(username)})


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


def create_user_with_key():
    """
    Create a user directory with a keyfile on the shared volume, data
    arriving in the payload of the request with a JSON payload.
    """
    username = username_from_request(request)

    if not username:
        response.status = 403
        return {'error': 'Permission denied'}

    pubkey = request.json.get('pubkey')

    if not pubkey:
        response.status = 400
        return {'error': 'Parameter \'pubkey\' not specified'}

    try:
        # Preliminary username check
        check_username(username)
        abs_home_path = normpath(os.path.join(PATH_PREFIX, username))
    except UsernameException as exc:
        response.status = exc.args[0]
        return exc.args[1]

    try:
        check_and_add(username)
    except UsernameException as exc:
        response.status = exc.args[0]
        return exc.args[1]

    # Do the actual creation
    store_pubkey(username, abs_home_path, pubkey)

    response.status = 201
    return {'response': 'Successful creation of user {0}.'.format(username)}


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
    run(host='0.0.0.0', reloader=True, server="paste")

if __name__ == '__main__':
    run_server()
