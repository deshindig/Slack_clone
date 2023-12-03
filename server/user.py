""" Imports for user file
"""
import hashlib
import os
import urllib.request
from PIL import Image

from server import auth
from server import data
from server.Error import ValueError

def user_profile(token, u_id, static_url="static/"):
    """ Returns a user's profile details
    """

    server_data = data.load_data()
    # checks if the token is valid
    auth.verify_token(token)
    user = server_data.return_user(u_id)
    return {
        "u_id": u_id,
        "email": user.get_email(),
        "name_first": user.get_name_first(),
        "name_last": user.get_name_last(),
        "handle_str": user.get_handle(),
        "profile_img_url": static_url + user.get_pfp_filename(),
    }

def user_profile_setname(token, name_first, name_last):
    """ Sets the user's first name and last name
    """

    server_data = data.load_data()
    user_id = auth.verify_token(token)
    server_data.return_user(user_id).set_name_first(name_first)
    server_data.return_user(user_id).set_name_last(name_last)
    data.save_data(server_data)

def user_profile_setemail(token, email):
    """ Setting the user's email
    """

    server_data = data.load_data()
    user_id = auth.verify_token(token)
    if server_data.is_registered_email(email):
        raise ValueError("Set email attempted with invalid email")
    server_data.return_user(user_id).set_email(email)
    data.save_data(server_data)

def user_profile_sethandle(token, handle_str):
    """ Updates the user's handle (display name)
    """

    server_data = data.load_data()
    user_id = auth.verify_token(token)
    if server_data.is_registered_handle(handle_str):
        raise ValueError("Handle is being used by another user")
    server_data.return_user(user_id).set_handle(handle_str)
    data.save_data(server_data)

def user_profiles_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    """ Crops and uploads a profile photo using a link from the web. Only JPEG
        format images can be uploaded.
    """

    u_id = auth.verify_token(token)
    server_data = data.load_data()
    WORKING_FILEPATH = data.ServerData.WORKING_FILEPATH
    STATIC_FILEPATH = data.ServerData.STATIC_FILEPATH
    hash_object = hashlib.md5(os.urandom(100))
    img_filename = hash_object.hexdigest() + ".jpeg"
    try:
        urllib.request.urlretrieve(img_url, WORKING_FILEPATH + img_filename)
    except:
        raise ValueError("The image url is invalid")
    img_obj = Image.open(WORKING_FILEPATH + img_filename)
    os.remove(WORKING_FILEPATH + img_filename)
    if (img_obj.format != "JPEG" and img_obj.format != "JPG"):
        raise ValueError("Image is not in JPEG format")
    width, height = img_obj.size
    if not (0 <= x_start <= width and
            x_start < x_end <= width and
            0 <= y_start <= height and
            y_start < y_end <= height):
        raise ValueError("Image crop bounds exceed image size")
    cropped = img_obj.crop((x_start, y_start, x_end, y_end))
    user = server_data.return_user(u_id)
    if user.get_pfp_filename() != data.ServerData.DEFAULT_PFP_FILENAME:
        os.remove(STATIC_FILEPATH + user.get_pfp_filename())
    saving = cropped.save(STATIC_FILEPATH + img_filename)
    user.set_pfp_filename(img_filename)
    data.save_data(server_data)
