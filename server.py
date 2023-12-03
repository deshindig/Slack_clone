""" Flask wrapper for Slackr server.

Most actual functionality is found in the server package, although some features
such as sending password reset emails (given a generated code) are implemented
here.
"""

import sys
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
from werkzeug.exceptions import HTTPException

from server import auth
from server import admin
from server import channel
from server import channels
from server import data
from server import user
from server import users
from server import message
from server import search
from server import standup
from server.Error import AccessError, ValueError

class SlackrHTTPException(HTTPException):
    """ Creates a custom HTTP exception that the front end can handle. """

    code = 400
    message = "No message specified"

def error_handler(err):
    """ Serialises error messages to conform with front-end interface. """

    response = err.get_response()
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = "application/json"

    return response

STATIC_RELATIVE_PATH = data.ServerData.STATIC_FILEPATH
SERVER_EMAIL = "1531project.byteMe.server@gmail.com"
APP_PASSWORD = "tyxqqclqdthbiwel"
APP = Flask(__name__, static_url_path="/"+STATIC_RELATIVE_PATH)
APP.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=SERVER_EMAIL,
    MAIL_PASSWORD=APP_PASSWORD,
)
APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(SlackrHTTPException, error_handler)
CORS(APP)

def send_success(return_data):
    """ Serialises the returned data from back-end functions in JSON. """

    return dumps(return_data)

@APP.route("/static/<path:path>")
def send_js(path):
    """ Route serving static files. """

    return send_from_directory("", path)

@APP.route("/echo/get", methods=["GET"])
def echo1():
    """ Description of function """

    return dumps({
        "echo" : request.args.get("echo"),
    })

@APP.route("/echo/post", methods=["POST"])
def echo2():
    """ Description of function """

    return dumps({
        "echo" : request.form.get("echo"),
    })

@APP.route("/auth/register", methods=["POST"])
def auth_register_route():
    """ TODO """

    email = request.form.get("email")
    password = request.form.get("password")
    name_first = request.form.get("name_first")
    name_last = request.form.get("name_last")
    try:
        register_data = auth.auth_register(email, password, name_first,
                                           name_last)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(register_data)

@APP.route("/auth/login", methods=["POST"])
def auth_login_route():
    """ TODO """

    print(request.host_url)
    email = request.form.get("email")
    password = request.form.get("password")
    try:
        login_data = auth.auth_login(email, password)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(login_data)

@APP.route("/auth/logout", methods=["POST"])
def auth_logout_route():
    """ TODO """

    token = request.form.get("token")
    logout_data = auth.auth_logout(token)

    return send_success(logout_data)

@APP.route("/auth/passwordreset/request", methods=["POST"])
def auth_passwordreset_request_route():
    """ Sends a password reset code to a registered email.

    Does nothing if email is not registered.
    """

    email = request.form.get("email")
    reset_code = auth.auth_passwordreset_request(email)
    if reset_code is not None:
        mail = Mail(APP)
        try:
            msg = Message("Slackr Password Reset",
                          sender="1531project.byteMe.server@gmail.com",
                          recipients=[email])
            msg.body = ("A request was submitted to reset the password for your"
                        " Slackr account.\n\n Please use this code to reset "
                        "your password: " + reset_code)
            mail.send(msg)
            return 'Mail sent!'
        except Exception as excinfo:
            raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route("/auth/passwordreset/reset", methods=["POST"])
def auth_passwordreset_reset_route():
    """ TODO """

    reset_code = request.form.get("reset_code")
    new_password = request.form.get("new_password")

    try:
        auth.auth_passwordreset_reset(reset_code, new_password)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route("/admin/userpermission/change", methods=["POST"])
def admin_userpermission_change_route():
    """ TODO """

    token = request.form.get("token")
    user_id = int(request.form.get("u_id"))
    permission_id = int(request.form.get("permission_id"))

    try:
        admin.admin_userpermission_change(token, user_id, permission_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route("/channel/invite", methods=["POST"])
def channel_invite_route():
    """ Invites a user to a channel. """

    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    u_id = int(request.form.get("u_id"))

    try:
        channel.channel_invite(token, channel_id, u_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route("/channel/details", methods=["GET"])
def channel_details_route():
    """ Returns details of a channel such as the name of the channel, members,
        and owners.
    """

    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    static_url = request.host_url + STATIC_RELATIVE_PATH

    try:
        channel_details = channel.channel_details(token, channel_id,
                                                  static_url)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(channel_details)

@APP.route("/channel/messages", methods=["GET"])
def channel_messages_route():
    """ Returns messages in a channel in a paginated manner. """

    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    start = int(request.args.get("start"))

    try:
        channel_messages = channel.channel_messages(token, channel_id, start)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(channel_messages)

@APP.route("/channel/leave", methods=["POST"])
def channel_leave_route():
    """ Removes the authorised user from the channel. """

    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))

    try:
        channel.channel_leave(token, channel_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route("/channel/join", methods=["POST"])
def channel_join_route():
    """ Adds the authorised user to a channel, given that they have sufficient
        privileges.
    """

    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))

    try:
        channel.channel_join(token, channel_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route("/channel/addowner", methods=["POST"])
def channel_addowner_route():
    """ Promotes a member of a channel to an owner, given the authorised user
        has sufficient privileges.
    """

    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    u_id = int(request.form.get("u_id"))

    try:
        channel.channel_addowner(token, channel_id, u_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route("/channel/removeowner", methods=["POST"])
def channel_removeowner_route():
    """ Demotes a member of a channel to an owner, given the authorised user
        has sufficient privileges.
    """

    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    u_id = int(request.form.get("u_id"))

    try:
        channel.channel_removeowner(token, channel_id, u_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route("/channels/list", methods=["GET"])
def channels_list_route():
    """ Returns a list of the ID and names of all the channels that the authorised
        user is in.
    """

    token = request.args.get("token")
    try:
        channels_info = channels.channels_list(token)
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(channels_info)

@APP.route("/channels/listall", methods=["GET"])
def channels_listall_route():
    """ Returns a list of the ID and names of all the channels on the server. """

    token = request.args.get("token")
    try:
        channels_info = channels.channels_listall(token)
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(channels_info)

@APP.route("/channels/create", methods=["POST"])
def channels_create_route():
    """ Creates a channel. A channel can only be set to private or public upon
        creation.
    """

    token = request.form.get("token")
    name = request.form.get("name")
    is_public = request.form.get("is_public")
    is_public = is_public == "true"

    try:
        channel_info = channels.channels_create(token, name, is_public)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(channel_info)

@APP.route('/user/profile', methods=['GET'])
def user_profile_route():
    """ Returns the profile information of a user. """

    u_id = int(request.args.get("u_id"))
    token = request.args.get("token")
    static_url = request.host_url + STATIC_RELATIVE_PATH

    try:
        profile_info = user.user_profile(token, u_id, static_url=static_url)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(profile_info)

@APP.route('/user/profile/setname', methods=['PUT'])
def user_profile_setname_route():
    """ Changes the authorised user's name. """

    token = request.form.get("token")
    first_name = request.form.get("name_first")
    last_name = request.form.get("name_last")

    try:
        user.user_profile_setname(token, first_name, last_name)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/user/profile/setemail', methods=['PUT'])
def user_profile_setemail_route():
    """ Changes the authorised user's email. """

    token = request.form.get("token")
    email = request.form.get("email")

    try:
        user.user_profile_setemail(token, email)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/user/profile/sethandle', methods=['PUT'])
def user_profile_sethandle_route():
    """ Changes the authorised user's handle. """

    token = request.form.get("token")
    handle = request.form.get("handle_str")

    try:
        user.user_profile_sethandle(token, handle)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/user/profiles/uploadphoto', methods=['POST'])
def user_profiles_uploadphoto_route():
    """ Uploads a profile image for the authorised user. """

    token = request.form.get("token")
    img_url = request.form.get("img_url")
    x_start = int(request.form.get("x_start"))
    y_start = int(request.form.get("y_start"))
    x_end = int(request.form.get("x_end"))
    y_end = int(request.form.get("y_end"))

    try:
        user.user_profiles_uploadphoto(token, img_url, x_start, y_start, x_end,
                                       y_end)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/users/all', methods=['GET'])
def users_all_route():
    """ Returns the profile information of all the users registered on the
        server.
    """

    token = request.args.get("token")
    static_url = request.host_url + STATIC_RELATIVE_PATH

    try:
        users_info = users.users_all(token, static_url)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(users_info)

#Message START
@APP.route('/message/send', methods=['POST'])
def message_send_route():
    """ Sends a message to a channel. """

    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    message_body = request.form.get("message")

    try:
        message_id = message.message_send(token, channel_id, message_body)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(message_id)

@APP.route('/message/sendlater', methods=['POST'])
def message_sendlaster_route():
    """ Sends a message to a channel at a given time in the future. """

    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    message_body = request.form.get("message")
    time_sent = int(request.form.get("time_sent"))

    try:
        message_id = message.message_sendlater(token, channel_id, message_body,
                                               time_sent)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(message_id)

@APP.route('/message/remove', methods=['DELETE'])
def message_remove_route():
    """ Removes a message from the channel it is posted in, given that the authorised
        user has sufficient privileges, or sent the message themselves.
    """

    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))

    try:
        message.message_remove(token, message_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/message/edit', methods=['PUT'])
def message_edit_route():
    """ Edits a message, given that the authorised user has sufficient privileges,
        or sent the message themselves. Messages edited to an empty body are
        deleted.
    """

    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))
    message_body = request.form.get("message")

    try:
        message.message_edit(token, message_id, message_body)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/message/react', methods=['POST'])
def message_react_route():
    """ Adds a reaction to a message. """

    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))
    react_id = int(request.form.get("react_id"))

    try:
        message.message_react(token, message_id, react_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/message/unreact', methods=['POST'])
def message_unreact_route():
    """ Removes a reaction from a message. """

    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))
    react_id = int(request.form.get("react_id"))

    try:
        message.message_unreact(token, message_id, react_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/message/pin', methods=['POST'])
def message_pin_route():
    """ Pins a message to the channel, given the authorised user has sufficient
        privileges.
    """

    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))

    try:
        message.message_pin(token, message_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/message/unpin', methods=['POST'])
def message_unpin_route():
    """ Unpins a message to the channel, given the authorised user has sufficient
        privileges.
    """

    token = request.form.get("token")
    message_id = int(request.form.get("message_id"))

    try:
        message.message_unpin(token, message_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route('/standup/start', methods=['POST'])
def standup_start_route():
    """ Begins a standup for a given duration. During a standup, messages sent
        to the standup are buffered in a queue and posted by the user who began
        the standup once the standup ends.
    """

    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    duration = int(request.form.get("length"))

    try:
        time_finish = standup.standup_start(token, channel_id, duration)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(time_finish)

@APP.route('/standup/active', methods=['GET'])
def standup_active_route():
    """ Returns whether a standup is active, and if it is, returns the time that
        the standup finishes.
    """

    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))

    try:
        standup_info = standup.standup_active(token, channel_id)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(standup_info)

@APP.route('/standup/send', methods=['POST'])
def standup_send_route():
    """ Sends a message to a standup. """

    token = request.form.get("token")
    channel_id = int(request.form.get("channel_id"))
    standup_message = request.form.get("message")

    try:
        standup.standup_send(token, channel_id, standup_message)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success({})

@APP.route("/search", methods=["GET"])
def search_route():
    """ Returns all the messages that contain the query string among the channels
        that the authorised user is in.
    """

    token = request.args.get("token")
    query_str = request.args.get("query_str")

    try:
        search_results = search.search(token, query_str)
    except ValueError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))
    except AccessError as excinfo:
        raise SlackrHTTPException(description=str(excinfo))

    return send_success(search_results)

if __name__ == '__main__':
    APP.run(port=(sys.argv[1] if len(sys.argv) > 1 else 5000))
