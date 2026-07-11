from flask_jwt_extended import create_access_token
from datetime import timedelta
from flask import current_app

def generate_token(user_id, username, role):
    identity = {'id': user_id, 'username': username, 'role': role}
    expires = timedelta(seconds=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    token = create_access_token(identity=identity, expires_delta=expires)
    return token