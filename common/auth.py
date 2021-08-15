
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from flask_httpauth import HTTPTokenAuth
from models.profile import Profile
token_auth = HTTPTokenAuth()


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


@token_auth.verify_token
def verify_token(token):
    return Profile.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)