"""
Auth module for service
"""

import flask

import jwt
# from jwt.algorithms import RSAAlgorithm
# from keycloak import KeycloakOpenID
# import requests

from candig_cnv_service.api.logging import structured_log as struct_log
from candig_cnv_service.api.logging import logger


def _report_proxy_auth_error(key, **kwargs):
    """
    Generate standard log message for warning:
    API access without
    :param **kwargs: arbitrary keyword parameters
    """
    message = 'Attempt to access with invalid proxy/api key: ' + key
    logger().warning(struct_log(action=message, **kwargs))


def auth_key(api_key, required_scopes=None):
    fc = flask.current_app.config
    # Allow CanDIG API gateway to handle auth (not for standalone use)
    if fc.get('AUTH_METHOD') == 'GATEWAY':
        # TODO: use gateway client certificate instead
        fh = flask.request.headers
        if not fh["Host"] == fc.get('GATEWAY_HOST'):
            _report_proxy_auth_error(api_key)
            return None
    # For now, any api_key to local app should work
    # TODO: refine auth methods
    return {}


def get_access_level():
    fh = flask.request.headers
    if not fh.get("Authorization"):
        _report_proxy_auth_error("NO AUTH HEADER")

    api_key = fh["Authorization"].split("Bearer ")[1]
    key = ""  # TODO
    pub_key = '-----BEGIN PUBLIC KEY-----\n'+key+'\n-----END PUBLIC KEY-----'

    decode = jwt.decode(api_key, pub_key, audience='ga4gh', algorithms='RS256')

    # decode = jwt.decode(api_key, verify=False)

    print(decode)

    # url = "http://0.0.0.0:8885/authz/acess"
    # headers = fh
    # request_handle = requests.Session()
    # resp = request_handle.get("{}".format(url), headers=headers, timeout=5)

    # print(resp)
    pass