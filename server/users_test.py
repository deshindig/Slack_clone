""" Unit tests for functions implementing features related to non-specific users. """

from server import data
from server.auth import auth_register, reset_auth_data
from server.users import users_all

def test_users_all_successful():
    """ Test that checks if the users_all function is successful, being able to see all the user's
    profile. We have to make users before calling function.
    """
    reset_auth_data()
    data.initialise_data()
    first_names = [
        "Jeffery",
        "Jeremy",
        "James",
    ]
    user1_info = auth_register("hello0@gmail.com", "oyvdhb585", "Jeffery", "Kondo")
    users_all(user1_info["token"])
    user2_info = auth_register("hello1@gmail.com", "oyvdhb586", "Jeremy", "Kale")
    users_all(user2_info["token"])
    user3_info = auth_register("hello2@gmail.com", "oyvdhb587", "James", "Kyle")
    users_all(user3_info["token"])
    users_info = users_all(user1_info["token"])
    users_all_names = [user["name_first"] for user in users_info["users"]]
    for name in first_names:
        assert name in users_all_names
