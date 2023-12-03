""" Contains all the channel operations that are performed on a single channel
    that already exists.
"""

from server import auth
from server import data
from server.Error import AccessError, ValueError

def channel_invite(token, channel_id, u_id):
    """ Invites a user to a channel. When successfully incited, the invited
        user is automatically added to the channel.

    ASSUMPTION: If the invited user is already in the channel, returns an error.
    """

    authorised_u_id = auth.verify_token(token)
    server_data = data.load_data()
    channel = server_data.return_channel(channel_id)
    user = server_data.return_user(u_id)
    if not channel.is_member(authorised_u_id):
        raise AccessError("Authorised user is not a member of the channel")
    if channel.is_member(u_id):
        raise ValueError("Invited user is already a member of the channel")
    user.add_channel(channel_id)
    channel.add_member(u_id)
    data.save_data(server_data)

def channel_details(token, channel_id, static_url="static/"):
    """ Returns all the details of a particular channel. This comprises the
        name of the channel, and the details of all the owners and members
        of the channel.
    """

    user_id = auth.verify_token(token)
    server_data = data.load_data()
    channel = server_data.return_channel(channel_id)
    if not channel.is_member(user_id):
        raise AccessError("Authorised user is not a member of the channel")
    user_obj = server_data.return_user
    return {
        "name": channel.get_name(),
        "owner_members": [{
            "u_id": u_id,
            "name_first": user_obj(u_id).get_name_first(),
            "name_last": user_obj(u_id).get_name_last(),
            "profile_img_url": static_url + user_obj(u_id).get_pfp_filename(),
        } for u_id in channel.get_owners()],
        "all_members": [{
            "u_id": u_id,
            "name_first": user_obj(u_id).get_name_first(),
            "name_last": user_obj(u_id).get_name_last(),
            "profile_img_url": static_url + user_obj(u_id).get_pfp_filename(),
        } for u_id in channel.get_members()],
    }

def channel_messages(token, channel_id, start):
    """ Returns a page of messages. This page of messages is 50 messages long,
        starting from the start index the function is provided.
    """

    user_id = auth.verify_token(token)
    server_data = data.load_data()
    channel = server_data.return_channel(channel_id)
    if not channel.is_member(user_id):
        raise AccessError("Authorised user is not a member of the channel")
    end = start + 50
    message_page = channel.get_messages(start, end)
    try:
        channel.get_messages(end, start + 50)
    except ValueError:
        end = -1
    msg_obj = server_data.return_message
    return {
        "messages": [{
            "message_id": id,
            "u_id": msg_obj(id).get_u_id(),
            "message": msg_obj(id).get_message_body(),
            "time_created": msg_obj(id).get_time_sent().timestamp(),
            "reacts": [{
                "react_id": react_id,
                "u_ids": u_ids,
                "is_this_user_reacted": user_id in u_ids,
            } for react_id, u_ids in msg_obj(id).get_reacts().items()],
            "is_pinned": msg_obj(id).is_pinned(),
        } for id in message_page],
        "start": start,
        "end": end,
    }

def channel_leave(token, channel_id):
    """ Removes a user from the channel. """

    user_id = auth.verify_token(token)
    server_data = data.load_data()
    user = server_data.return_user(user_id)
    channel = server_data.return_channel(channel_id)
    user.remove_channel(channel_id)
    channel.remove_member(user_id)
    data.save_data(server_data)

def channel_join(token, channel_id):
    """ Allows a user to join a channel if the channel is public. If the
        channel is private, the user must have owner or admin privileges.

    ASSUMPTION: If the user is already in the channel, returns an error.
    """

    user_id = auth.verify_token(token)
    server_data = data.load_data()
    user = server_data.return_user(user_id)
    channel = server_data.return_channel(channel_id)
    if user.get_permission_id() == data.User.USER_ID and not channel.is_public():
        raise AccessError("Cannot join private channel with regular user permissions.")
    if channel.is_member(user_id):
        raise ValueError("User is already a member of the channel")
    user.add_channel(channel_id)
    channel.add_member(user_id)
    data.save_data(server_data)

def channel_addowner(token, channel_id, u_id):
    """ Promotes a user of the channel to an owner. Promoter must have owner
        privileges.
    """

    authorised_u_id = auth.verify_token(token)
    server_data = data.load_data()
    channel = server_data.return_channel(channel_id)
    authorised_user = server_data.return_user(authorised_u_id)
    if (not channel.is_owner(authorised_u_id) and
            authorised_user.get_permission_id() != data.User.OWNER_ID):
        raise AccessError("Authorised user is not a owner of the channel or a Slackr owner")
    if channel.is_owner(u_id):
        raise ValueError("User is already owner of the channel")
    channel.add_owner(u_id)
    data.save_data(server_data)

def channel_removeowner(token, channel_id, u_id):
    """ Demotes an owner to a regular user. Demoter must be an owner. """

    authorised_u_id = auth.verify_token(token)
    server_data = data.load_data()
    channel = server_data.return_channel(channel_id)
    authorised_user = server_data.return_user(authorised_u_id)
    if (not channel.is_owner(authorised_u_id) and
            authorised_user.get_permission_id() != data.User.OWNER_ID):
        raise AccessError("Authorised user is not a owner of the channel or a Slackr owner")
    if not channel.is_owner(u_id):
        raise ValueError("User is not an owner of the channel")
    channel.remove_owner(u_id)
    data.save_data(server_data)
