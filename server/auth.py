""" Contains all the functions pertaining to authentication and authorication.
"""
import binascii
import datetime
import hashlib
import os
import random
import re
import string

import jwt

from server import data
from server.Error import AccessError, ValueError

AUTH_DATA = {
    "jwt_secret": hashlib.sha256(os.urandom(100)).hexdigest(),
    "invalid_tokens": set(),
    "reset_codes": {},
}

def is_valid_email(email):
    """ Checks if email is valid. """

    email_reg_string = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.search(email_reg_string, email)

def get_auth_data():
    """ Returns the data used for authorisation and authentication. This data
        is not saved when the server goes down.
    """

    global AUTH_DATA
    return AUTH_DATA

def reset_auth_data():
    """ Resets the data used for authoration and authentication. Useful for
        unit testing. """

    global AUTH_DATA
    AUTH_DATA = {
        "jwt_secret": hashlib.sha256(os.urandom(100)).hexdigest(),
        "invalid_tokens": set(),
        "reset_codes": {},
    }

def generate_token(user_id):
    """ Generates a new session token for a user. """

    auth_data = get_auth_data()
    payload = {
        "u_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "padding": binascii.hexlify(os.urandom(64)).decode("ascii")
    }
    encoded_jwt = jwt.encode(payload, auth_data["jwt_secret"], algorithm="HS256")
    encoded_jwt = encoded_jwt.decode("ascii")

    return encoded_jwt

def invalidate_token(token):
    """ Makes a session token invalid so that attempting to access features
        requiring authorisation using this token will be unsuccessful.
    """

    auth_data = get_auth_data()
    auth_data["invalid_tokens"].add(token)

def verify_token(token):
    """ Verifies a token.

    Returns the u_id of the user, and raises an error if the token is invalid.
    """

    auth_data = get_auth_data()
    if token in auth_data["invalid_tokens"]:
        raise AccessError("Invalid token")
    try:
        payload = jwt.decode(token.encode("ascii"), auth_data["jwt_secret"], algorithms=["HS256"])
    except:
        raise AccessError("Invalid token")

    return payload["u_id"]

def auth_login(email, password):
    """ Logs the user in using an email and password. """

    server_data = data.load_data()
    if not is_valid_email(email):
        raise ValueError("Login attempted with invalid email")
    user_id = server_data.get_u_id_from_email(email)
    if not server_data.return_user(user_id).verify_password(password):
        raise ValueError("Login attempted with incorrect password")

    return {
        "u_id": user_id,
        "token": generate_token(user_id),
    }

def auth_logout(token):
    """ Logs the user out, invalidating their session token. """

    try:
        verify_token(token)
    except AccessError:
        return {"is_success": False}
    invalidate_token(token)

    return {"is_success": True}

def auth_register(email, password, name_first, name_last):
    """ Registers a user and generates a default token.

    A user is identified by a user ID. A unique handle is generated for the
    user by appending a random 3-digit code.
    """

    server_data = data.load_data()
    if server_data.is_registered_email(email):
        raise ValueError("Registration attempted with unavailable email")
    user_id = server_data.get_new_u_id()
    user = data.User(user_id, email, password, name_first, name_last)
    user_handle = user.get_name_first() + user.get_name_last()
    # Cuts long user handles down to 20 characters.
    if len(user_handle) > 20:
        user_handle = user_handle[:20]
    # If a handle is not unique, cuts it down to 17 characters to add the
    # 3-digit suffix that makes it unique.
    if server_data.is_registered_handle(user_handle) and len(user_handle) > 17:
        user_handle = user_handle[:17]
    user_handle = server_data.generate_unique_handle(user_handle)
    user.set_handle(user_handle)
    #The first user registered is the Slackr owner.
    if server_data.get_u_id_counter() == 1:
        user.set_permission_id(data.User.OWNER_ID)
    user.set_pfp_filename(server_data.DEFAULT_PFP_FILENAME)
    server_data.register_user(user)
    data.save_data(server_data)

    return {
        "u_id": user_id,
        "token": generate_token(user_id),
    }

def auth_passwordreset_request(email):
    """ Returns a password reset code.

    Does nothing if the email is not registered.
    Code is valid until it is used, or the auth data resets.
    """

    server_data = data.load_data()
    auth_data = get_auth_data()
    if server_data.is_registered_email(email):
        # Generates a unique reset code.
        while True:
            reset_code = "".join(random.choices(string.ascii_letters + string.digits, k=6))
            if reset_code not in auth_data["reset_codes"]:
                break
        auth_data["reset_codes"][reset_code] = server_data.get_u_id_from_email(email)

    return reset_code

def auth_passwordreset_reset(reset_code, new_password):
    """ Resets a password given a valid reset code

    If the reset code is invalid, or the password does not meet specifications,
    then an error is raised.
    """

    server_data = data.load_data()
    auth_data = get_auth_data()
    if reset_code not in auth_data["reset_codes"]:
        raise ValueError("Invalid reset code")
    u_id = auth_data["reset_codes"][reset_code]
    server_data.return_user(u_id).set_password(new_password)
    data.save_data(server_data)
    del auth_data["reset_codes"][reset_code]
