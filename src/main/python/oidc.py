import os
from requests import request
from datetime import datetime
from calendar import timegm


AUTH_URL = "<your-auth-server>"


def init_auth_url():
    global AUTH_URL
    AUTH_URL = os.environ['AUTH_URL']


def username_from_request(http_request):

    authorization_header = http_request.headers.get('Authorization')
    if not authorization_header:
        return None

    if not authorization_header.startswith('Bearer '):
        return None

    access_token = authorization_header.split('Bearer ', 1)[1]

    user_info = fetch_user_info(access_token)

    if validate_user_info(user_info):
        return user_info['sub']
    else:
        return None


def fetch_user_info(access_token):

    user_info = request(
        'GET', AUTH_URL,
        headers={
            'Authorization': 'Bearer ' + access_token
        }).json()

    return user_info


def validate_user_info(user_info):

    # The Issuer Identifier for the OpenID Provider (which is typically
    # obtained during Discovery) MUST exactly match the value of the iss
    # (issuer) Claim.
    valid_issuer = \
        user_info['iss'] == AUTH_URL

    # The Client MUST validate that the aud (audience) Claim contains
    # its client_id value registered at the Issuer identified by the iss
    # (issuer) Claim as an audience. The aud (audience) Claim MAY
    # contain an array with more than one element. The ID Token MUST be
    # rejected if the ID Token does not list the Client as a valid
    # audience, or if it contains additional audiences not trusted by
    # the Client.
    valid_audience = user_info['aud'] == 'jumpauth'

    # The current time MUST be before the time represented by the exp Claim.
    not_expired = timegm(datetime.utcnow().utctimetuple()) <= user_info['exp']

    return valid_issuer and valid_audience and not_expired
