""" Contains all the functions operating on many users. """

from server import auth
from server import data
from server import user

def users_all(token, static_url="static/"):
    """ Returns the profile info of all the users on the Slackr. """

    auth.verify_token(token)
    server_data = data.load_data()
    return {
        "users": [user.user_profile(token, u_id, static_url) \
                  for u_id in server_data.get_all_u_id()]
    }
