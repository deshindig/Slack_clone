""" Contains all the functions implementing the search feature. """

from server import auth
from server import data

def search(token, query_str):
    """ Returns all the messages that a query string is found in. Only searches
        the channels that the authorised user is in.
    """

    user_id = auth.verify_token(token)
    server_data = data.load_data()
    message_info = {
        "messages": [],
    }

    user = server_data.return_user(user_id)
    for channel_id in user.get_channels():
        for msg_id in server_data.return_channel(channel_id):
            msg = server_data.return_message(msg_id)
            if query_str in msg.get_message_body():
                message_info["messages"].append({
                    "message_id": msg_id,
                    "u_id": msg.get_u_id(),
                    "message": msg.get_message_body(),
                    "time_created": msg.get_time_sent().timestamp(),
                    "reacts": [{
                        "react_id": react_id,
                        "u_ids": u_ids,
                        "is_this_user_reacted": user_id in u_ids,
                    } for react_id, u_ids in msg.get_reacts().items()],
                    "is_pinned": msg.is_pinned(),
                })

    return message_info
