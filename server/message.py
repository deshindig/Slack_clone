""" Contains all messaging-related functions. """

import datetime
import threading

from server import auth
from server import data
from server.Error import AccessError, ValueError

def is_valid_message_body(message_body):
    """ Checks if message is of valid length. """

    if len(message_body) > 1000:
        return False
    return True

def message_send(token, channel_id, message_body):
    """ Sends a message. """

    u_id = auth.verify_token(token)
    server_data = data.load_data()
    if not is_valid_message_body(message_body):
        raise ValueError("Exceed 1000 word limit")
    channel = server_data.return_channel(channel_id)
    if not channel.is_member(u_id):
        raise AccessError("User is not member of the channel")
    time_sent = datetime.datetime.now()
    message_id = server_data.get_new_message_id()
    message_obj = data.Message(message_id, u_id, channel_id, message_body, time_sent)
    server_data.register_message(message_obj)
    channel.add_message(message_id)
    data.save_data(server_data)
    return {
        "message_id": message_id
    }

def send_timed_message(channel_id, message_id):
    """ Store the message into the channel class after the time is met for
    message_sendlater.
    """

    server_data = data.load_data()
    server_data.return_channel(channel_id).add_message(message_id)
    data.save_data(server_data)

def message_sendlater(token, channel_id, message_body, time_sent):
    """ Send message at the time given by the user. """

    u_id = auth.verify_token(token)
    server_data = data.load_data()
    if not is_valid_message_body(message_body):
        raise ValueError("Exceed 1000 word limit")
    channel = server_data.return_channel(channel_id)
    if not channel.is_member(u_id):
        raise AccessError("User is not member of the channel")
    current_time_epoch = int(datetime.datetime.now().timestamp())
    epoch_diff = time_sent - current_time_epoch
    if epoch_diff < 0:
        raise ValueError("Time sent is in the past")
    message_id = server_data.get_new_message_id()
    message_obj = data.Message(message_id, u_id, channel_id, message_body,
                               datetime.datetime.fromtimestamp(time_sent))
    server_data.register_message(message_obj)
    data.save_data(server_data)

    # Starts the timer thread that will send the message at the specified time.
    timer1 = threading.Timer(epoch_diff, send_timed_message, args=[channel_id, message_id])
    timer1.start()

    return {
        "message_id": message_id
    }

def message_remove(token, message_id):
    """ Delete message of a specified ID. """

    u_id = auth.verify_token(token)
    server_data = data.load_data()
    message = server_data.return_message(message_id)
    if (message.get_u_id() != u_id and
            server_data.return_user(u_id).get_permission_id() == data.User.USER_ID):
        raise AccessError("User does not have permission")
    channel_id = message.get_channel_id()
    server_data.return_channel(channel_id).remove_message(message_id)
    server_data.delete_message(message_id)
    data.save_data(server_data)

def message_edit(token, message_id, message_body):
    """ Edits a message of a specified id. """

    u_id = auth.verify_token(token)
    server_data = data.load_data()
    if not is_valid_message_body(message_body):
        raise ValueError("Exceed 1000 word limit")
    message = server_data.return_message(message_id)
    if (message.get_u_id() != u_id and
            server_data.return_user(u_id).get_permission_id() == data.User.USER_ID):
        raise AccessError("User does not have permission")
    if message_body == "":
        message_remove(token, message_id)
    else:
        message.set_message_body(message_body)
        data.save_data(server_data)

def message_react(token, message_id, react_id):
    """ Adds a reaction given a react ID to a message given a message ID. """

    u_id = auth.verify_token(token)
    server_data = data.load_data()
    message = server_data.return_message(message_id)
    if react_id != 1:
        raise ValueError("Invalid react id")
    message.add_react(u_id, react_id)
    data.save_data(server_data)

def message_unreact(token, message_id, react_id):
    """ Removes a reaction given a react ID to a message given a message ID. """

    auth.verify_token(token)
    server_data = data.load_data()
    message = server_data.return_message(message_id)
    if react_id != 1:
        raise ValueError("Invalid react id")
    message.remove_react(react_id)
    data.save_data(server_data)

def message_pin(token, message_id):
    """ Pins message given by message ID. """

    u_id = auth.verify_token(token)
    server_data = data.load_data()
    message = server_data.return_message(message_id)
    user = server_data.return_user(u_id)
    if (user.get_permission_id() != data.User.ADMIN_ID and
            user.get_permission_id() != data.User.OWNER_ID):
        raise AccessError("User does not have permission")
    if message.is_pinned():
        raise ValueError("Message is already pinned")
    message.pin()
    data.save_data(server_data)

def message_unpin(token, message_id):
    """ Unpins message given by message_id. """

    u_id = auth.verify_token(token)
    server_data = data.load_data()
    message = server_data.return_message(message_id)
    user = server_data.return_user(u_id)
    if (user.get_permission_id() != data.User.ADMIN_ID and
            user.get_permission_id() != data.User.OWNER_ID):
        raise AccessError("User does not have permission")
    if not message.is_pinned():
        raise ValueError("Message is already unpinned")
    message.unpin()
    data.save_data(server_data)
