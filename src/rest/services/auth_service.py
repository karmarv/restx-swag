import os
import logging

import re
import jwt
import datetime
import hashlib

from flask import request, make_response
from flask_restx import Namespace, Resource, fields

from rest.services import config, utils
from rest.services.exceptions import ValidationException

from rest.services.data.auth import create_user, read_user, current_user
from rest.services.data.auth import create_refresh_token, read_refresh_token, update_refresh_token

log = logging.getLogger("rx")
api = Namespace('auth', description='Operations related Authentication and Authorization')


register_model = api.model('Register', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

return_token_model = api.model('ReturnToken', {
    'access_token': fields.String(required=True),
    'refresh_token': fields.String(required=True)
})

# -------------------------------------- #
# API Controllers and query param parser #
# -------------------------------------- #
@api.route('/register')
class Register(Resource):
    @api.expect(register_model, validate=True)
    @api.response(400, 'username or password incorrect')
    def post(self):
        """Register a user for the first time with username and password"""
        if not re.search(config.JWT_USERNAME_REGEXP, api.payload['username']):
            raise ValidationException(error_field_name='username',
                                      message='4-16 symbols, can contain A-Z, a-z, 0-9, _ \
                                      (_ can not be at the begin/end and can not go in a row (__))')
        if not re.search(config.JWT_PASSWORD_REGEXP, api.payload['password']):
            raise ValidationException(error_field_name='password',
                                      message='6-64 symbols, required upper and lower case letters. Can contain !@#$%_')

        user = create_user(api.payload['username'], api.payload['password'])
        user_json = user.serialize()
        user_json["password_hash"] = "[Hidden]"
        response = make_response(user_json)
        return response


@api.route('/login')
class Login(Resource):
    @api.expect(register_model)
    @api.response(200, 'Success', return_token_model)
    @api.response(401, 'Incorrect username or password')
    def post(self):
        """
        Login for obtaining authorized access token
        This API implemented JWT. Token's payload contain:
        'uid' (user id),
        'exp' (expiration date of the token),
        'iat' (the time the token is generated)
        """
        user = read_user(api.payload['username'])
        if not user:
            api.abort(401, 'Incorrect username or password')

        from werkzeug.security import check_password_hash
        if check_password_hash(user.password_hash, api.payload['password']):
            _access_token = jwt.encode({'uid': user.id,
                                        'exp': datetime.datetime.now(datetime.timezone.utc) 
                                                + datetime.timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRY_MINUTES),
                                        'iat': datetime.datetime.now(datetime.timezone.utc)},
                                        config.JWT_SECRET_KEY,
                                        algorithm=config.JWT_ALGORITHM)
            _refresh_token = jwt.encode({'uid': user.id,
                                         'exp': datetime.datetime.now(datetime.timezone.utc) 
                                                + datetime.timedelta(days=config.JWT_REFRESH_TOKEN_EXPIRY_DAYS),
                                         'iat': datetime.datetime.now(datetime.timezone.utc)},
                                         config.JWT_SECRET_KEY,
                                         algorithm=config.JWT_ALGORITHM)

            user_agent_string = request.user_agent.string.encode('utf-8')
            user_agent_hash = hashlib.md5(user_agent_string).hexdigest()
            # Create a refresh token in database
            create_refresh_token(user.id, user_agent_hash, _refresh_token)
            return make_response({'access_token': _access_token, 'refresh_token': _refresh_token})

        api.abort(401, 'Incorrect username or password')


@api.route('/refresh')
class Refresh(Resource):
    @api.expect(api.model('RefreshToken', {'refresh_token': fields.String(required=True)}), validate=True)
    @api.response(200, 'Success', return_token_model)
    def post(self):
        """Refresh the access token for continued access"""
        _refresh_token = api.payload['refresh_token']

        try:
            payload_jwt = jwt.decode(_refresh_token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
            log.info(payload_jwt)
            refresh_token = read_refresh_token(user_id=payload_jwt['uid'], refresh_token=_refresh_token)
            if not refresh_token:
                raise jwt.InvalidIssuerError

            # Generate new pair
            _access_token = jwt.encode({'uid': refresh_token.user_id,
                                        'exp': datetime.datetime.now(datetime.timezone.utc) 
                                                + datetime.timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRY_MINUTES),
                                        'iat': datetime.datetime.now(datetime.timezone.utc)},
                                        config.JWT_SECRET_KEY,
                                        algorithm=config.JWT_ALGORITHM)
            _refresh_token = jwt.encode({'uid': refresh_token.user_id,
                                         'exp': datetime.datetime.now(datetime.timezone.utc) 
                                                + datetime.timedelta(days=config.JWT_REFRESH_TOKEN_EXPIRY_DAYS),
                                         'iat': datetime.datetime.now(datetime.timezone.utc)},
                                        config.JWT_SECRET_KEY,
                                        algorithm=config.JWT_ALGORITHM)

            refresh_token.refresh_token = _refresh_token
            update_refresh_token(refresh_token)
            return make_response({'access_token': _access_token, 'refresh_token': _refresh_token})
        except jwt.ExpiredSignatureError as e:
            raise e
        except (jwt.DecodeError, jwt.InvalidTokenError)as e:
            raise e
        except:
            api.abort(401, 'Unknown token error')
            


# ------------------------- #
# Authentication Decorator  #
# ------------------------- #
def token_required(f):
    """Decorator for authorizing the presented bearer access_token in header"""
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        session_user = None
        if auth_header:
            try:
                access_token = auth_header.split(' ')

                try:
                    log.info(access_token)
                    token = jwt.decode(access_token[1].strip(), config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
                    log.info(token)
                    session_user = current_user(token['uid'])
                    log.info(session_user)
                except jwt.ExpiredSignatureError as e:
                    raise e
                except (jwt.DecodeError, jwt.InvalidTokenError) as e:
                    raise e
                except:
                    api.abort(401, 'Unknown token error')

            except IndexError:
                raise jwt.InvalidTokenError
        else:
            api.abort(403, 'Token required')
        return f(*args, **kwargs, current_user=session_user)
    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


@api.route('/protected')
class Protected(Resource):
    @token_required
    def get(self, current_user):
        """An access token based protected test resource for obtaining user identifier. This resource is for test only"""
        return make_response({'level': 'protected', 'uid': current_user.id})