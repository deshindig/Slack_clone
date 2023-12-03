""" Contains the channel operations that are not performed on a single
    pre-existing channel.
"""

from server import auth
from server import data

def channels_list(token):
    """ Returns a list of all the channels that a user is in. """

    user_id = auth.verify_token(token)
    server_data = data.load_data()
    user = server_data.return_user(user_id)
    channel_obj = server_data.return_channel
    channels_info = [{
        "channel_id": id,
        "name": channel_obj(id).get_name(),
    } for id in user.get_channels()]
    return {
        "channels": channels_info
    }

def channels_listall(token):
    """ Returns a list of all the channels on the Slackr."""

    auth.verify_token(token)
    server_data = data.load_data()
    channel_obj = server_data.return_channel
    channels_info = [{
        "channel_id": id,
        "name": channel_obj(id).get_name(),
    } for id in server_data.get_all_channel_id()]
    return {
        "channels": channels_info
    }

def channels_create(token, name, is_public):
    """ Creates a new channel. The channel can be set to private or public
        when creating the channel.
    """

    user_id = auth.verify_token(token)
    server_data = data.load_data()
    channel_id = server_data.get_new_channel_id()
    channel = data.Channel(channel_id, user_id, name, is_public)
    server_data.register_channel(channel)
    user = server_data.return_user(user_id)
    user.add_channel(channel_id)
    data.save_data(server_data)
    return {
        "channel_id": channel_id
    }
