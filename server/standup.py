""" Contains all the functions that implement the standup feture. """

import datetime
import threading

from server import auth
from server import data
from server import message
from server.Error import AccessError, ValueError

# Stores the standup data as a global dictionary.

# Standup data is not persistent, as the server needs to be running to time the
# end of a standup.
STANDUP_DATA = {
    # channel_id: {
    #     "time_finish":
    #     "message_queue": [ f"{name}: {message}" ]
    # }
}

def reset_standup_data():
    global STANDUP_DATA
    STANDUP_DATA = {}

def get_standup_data():
    """ Returns the standup data. """

    global STANDUP_DATA
    return STANDUP_DATA

def standup_end(channel_id, user_id):
    """ Called when the standup timer thread finishes.

    An automated message is sent using the account of the user who began the
    standup. This message contains all the standup messages sent with the name
    of the user who sent the standup message.
    """

    server_data = data.load_data()
    standup_data = get_standup_data()
    standup_body = "Standup:\n\n"
    standup_body += "\n".join(standup_data[channel_id]["message_queue"])
    time_sent = datetime.datetime.now()
    message_id = server_data.get_new_message_id()
    message_obj = data.Message(message_id, user_id, channel_id, standup_body, time_sent)
    server_data.register_message(message_obj)
    server_data.return_channel(channel_id).add_message(message_id)
    del standup_data[channel_id]
    data.save_data(server_data)


def standup_start(token, channel_id, length):
    """ Starts a standup for a specified length in a specified channel.

    The standup is timed using a timer thread. When this thread expires,
    standup_end() is called.
    """

    user_id = auth.verify_token(token)
    server_data = data.load_data()
    channel = server_data.return_channel(channel_id)
    if not channel.is_member(user_id):
        raise AccessError("Authorised user is not a member of the channel")
    standup_data = get_standup_data()
    if channel_id in standup_data:
        raise ValueError("A standup is already active in the current channel")
    standup_timer = threading.Timer(length, standup_end, args=[channel_id, user_id])
    time_finish = (datetime.datetime.now() + datetime.timedelta(seconds=length)).timestamp()
    standup_data[channel_id] = {}
    standup_data[channel_id]["time_finish"] = time_finish
    standup_data[channel_id]["message_queue"] = []
    standup_timer.start()
    return {
        "time_finish": time_finish
    }

def standup_send(token, channel_id, message_body):
    """ During an active standup, sends a message that gets buffered in a queue.

    When the standup finished, all the messages in the queue are sent in a single
    standup message by the user who started the standup.
    """

    user_id = auth.verify_token(token)
    server_data = data.load_data()
    channel = server_data.return_channel(channel_id)
    if not channel.is_member(user_id):
        raise AccessError("Authorised user is not a member of the channel")
    standup_data = get_standup_data()
    if channel_id not in standup_data:
        raise ValueError("No standup running in current channel")
    if not message.is_valid_message_body(message_body):
        raise ValueError("Invalid message entered with over 1000 characters")
    user = server_data.return_user(user_id)
    name = user.get_name_first() + " " + user.get_name_last()
    message_text = f"{name}: {message_body}"
    standup_data[channel_id]["message_queue"].append(message_text)

def standup_active(token, channel_id):
    """ Returns whether a standup is active in a channel. If so, return the
        time that the standup finishes.
    """

    auth.verify_token(token)
    server_data = data.load_data()
    server_data.return_channel(channel_id)
    standup_data = get_standup_data()
    if channel_id not in standup_data:
        is_active = False
        time_finish = None
    else:
        is_active = True
        time_finish = standup_data[channel_id]["time_finish"]
    return {
        "is_active": is_active,
        "time_finish": time_finish
    }
