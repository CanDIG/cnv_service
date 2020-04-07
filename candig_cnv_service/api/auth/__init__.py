"""
Auth module for service
"""

# import jwt
from jwt.algorithms import RSAAlgorithm
from keycloak import KeycloakOpenID
import requests

from candig_cnv_service.api.exceptions import HandlerError

_HANDLER = None


class KeyCloakHandler:

    def __init__(self, config):
        self.config = config
        self.conn = self.connect_to_keycloak()
        self.key_set = self.get_key_set()
        self.public_key = RSAAlgorithm.from_jwk(self.key_set)

    def connect_to_keycloak(self):
        keycloak_openid = KeycloakOpenID(
            server_url=self.config['KC_SERVER'] + "/auth/",
            client_id=self.configs['OIDC_CLIENT'],
            realm_name=self.config['KC_REALM'],
            client_secret_key=self.config['OIDC_CLIENT_SECRET'],
            verify=True
        )
        return keycloak_openid

    def get_key_set(self):
        key_response = requests.get(self.conn.well_know()['jwks_uri'])
        print(key_response)


def create_handler(config):
    global _HANDLER
    _HANDLER = KeyCloakHandler(config)


def get_handler():
    global _HANDLER
    if not _HANDLER:
        raise HandlerError
    return _HANDLER
