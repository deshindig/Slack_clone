""" Unit tests for all functions implementing the standup feature. """

from time import sleep

import pytest

from server.Error import AccessError, ValueError
from server.standup import standup_start, standup_send, reset_standup_data, standup_active
from server.auth import auth_register, reset_auth_data
from server.channels import channels_create
from server import data
from server.channel import channel_join, channel_invite, channel_messages

def func_startup():
    """ Resets all the data and then reinitialise it again
    """
    reset_auth_data()
    reset_standup_data()
    data.initialise_data()

def user_channel_create(is_public):
    """ Creates a user and a channel. The channel created can be either public or private
    """
    if is_public:
        user_info = auth_register("monopoly@gmail.com", "1a2b3c4d", "Felix", "Brown")
        channel_name = "Happy Channel"
        channel_id = channels_create(user_info["token"], channel_name, True)
    else:
        user_info = auth_register("waterhealthy90@gmail.com", "lightbulb58", "Alice", "Barns")
        channel_name = "Dead End"
        channel_id = channels_create(user_info["token"], channel_name, False)
    return user_info, channel_id

def test_standup_start_invalid_channel():
    """ Tests to see if we are unable to start a standup
    Check if there is invalid channel (id -based) of a public/private channel
    """
    func_startup()
    user1_info, channel_id = user_channel_create(True)
    with pytest.raises(ValueError) as excinfo:
        standup_start(user1_info["token"], channel_id["channel_id"] + 3 * 4, 1)
    assert "Invalid channel id" in str(excinfo.value)
    # Case for private channel
    user2_info, channel_id = user_channel_create(False)
    with pytest.raises(ValueError) as excinfo:
        standup_start(user2_info["token"], channel_id["channel_id"] + 3 * 4, 1)
    assert "Invalid channel id" in str(excinfo.value)

def test_standup_start_unauthorised_member_public():
    """ Check if an authorised user is not a member of the channel where the message is
    This case if for when the channel is public
    """
    func_startup()
    channel_id = user_channel_create(True)[1]
    # if user2 is not in channel, then AccessError
    user2_info = auth_register("kittycat@gmail.com", "butterflies234", "Sophie", "Reid")
    with pytest.raises(AccessError) as excinfo:
        # start the standup (second user) - error occur
        standup_start(user2_info["token"], channel_id["channel_id"], 1)
    assert "Authorised user is not a member of the channel" in str(excinfo.value)

def test_standup_start_unauthorised_member_private():
    """ Check if an authorised user is not a member of the channel where the message is
    This case if for when the channel is private
    AccessError occur when authorised member in is not channel ("Attempt to start
    standup has failed due to user not in current channel")
    """
    func_startup()
    # register account
    channel_id = user_channel_create(False)[1]
    # if user2 is not in channel, then AccessError
    user2_info = auth_register("waterhealthy@gmail.com", "lightbulb488", "Anna", "Bell")
    with pytest.raises(AccessError) as excinfo:
        # start the standup (second user) - error occur
        standup_start(user2_info["token"], channel_id["channel_id"], 1)
    assert "Authorised user is not a member of the channel" in str(excinfo.value)

def test_standup_start_successful():
    """ Tests for standup_start to be successful
    If standup_send works without errors, then standup_start must have been successful
    """
    func_startup()
    # Testing for the case when the channel is public
    user1_info, channel_id = user_channel_create(True)
    standup_start(user1_info["token"], channel_id["channel_id"], 1)
    standup_send(user1_info["token"], channel_id["channel_id"], "I love milk")
    active1_info = standup_active(user1_info["token"], channel_id["channel_id"])
    assert active1_info["is_active"]
    # Testing for the case when the channel is private
    user2_info, channel_id = user_channel_create(False)
    standup_start(user2_info["token"], channel_id["channel_id"], 1)
    standup_send(user2_info["token"], channel_id["channel_id"], "Yay, its Friday")
    active2_info = standup_active(user2_info["token"], channel_id["channel_id"])
    assert active2_info["is_active"]
    sleep(1)

def test_standup_send_failed_channel_no_exist():
    """ Tests to see if standup_send fails due to the channel not existing (id-based)
    ValueError occurs once channel does not exist ("Attempt to send a standup failed
    due to channel not existing")
    """
    func_startup()
    # Case for public channel
    user1_info, channel_id = user_channel_create(True)
    standup_start(user1_info["token"], channel_id["channel_id"], 1)
    with pytest.raises(ValueError) as excinfo:
        standup_send(user1_info["token"], channel_id["channel_id"] + 100,
                     "Buffering message now")
    assert "Invalid channel id" in str(excinfo.value)
    # Case for private channel
    user2_info, channel_id = user_channel_create(False)
    with pytest.raises(ValueError) as excinfo:
        standup_send(user2_info["token"], channel_id["channel_id"] + 100,
                     "Buffering message now")
    assert "Invalid channel id" in str(excinfo.value)
    sleep(1)

def test_standup_send_fail_long_message_public():
    """ Test to check if are not able to send a message to standup in public channel
    If a message is more than 1000 characters, then ValueError will occur
    Example: message = "a" * 1001,   message = "!" * 1001,   message = "Lost" * 500
    ValueError ("Attempt to send message to standup failed due to characters over
    1000")
    """
    func_startup()
    # Case for public channel
    user_info, channel_id = user_channel_create(True)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    with pytest.raises(ValueError) as excinfo:
        standup_send(user_info["token"], channel_id["channel_id"], "a" * 1001)
    assert "Invalid message" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        standup_send(user_info["token"], channel_id["channel_id"], "!" * 1001)
    assert "Invalid message" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        standup_send(user_info["token"], channel_id["channel_id"], "Lost" * 500)
    assert "Invalid message" in str(excinfo.value)
    sleep(1)

def test_standup_send_fail_long_message_private():
    """ Test to check if are not able to send a message to standup in private channel
    If a message is more than 1000 characters, then ValueError will occur
    Example: message = "a" * 1001,   message = "!" * 1001,   message = "Lost" * 500
    ValueError ("Attempt to send message to standup failed due to characters over
    1000")
    """
    func_startup()
    # Case for private channel
    user_info, channel_id = user_channel_create(False)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    with pytest.raises(ValueError) as excinfo:
        standup_send(user_info["token"], channel_id["channel_id"], "a" * 1001)
    assert "Invalid message" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        standup_send(user_info["token"], channel_id["channel_id"], "!" * 1001)
    assert "Invalid message" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        standup_send(user_info["token"], channel_id["channel_id"], "Lost" * 500)
    assert "Invalid message" in str(excinfo.value)
    sleep(1)

def test_standup_send_failed_unauthorised_public():
    """ Test to see that a user is not in a channel where the message is within
    This is for when a channel is public
    AccessError occur as ("Attempt to send message to standup channel failed, due to
    user not in current channel")
    """
    func_startup()
    user1_info, channel_id = user_channel_create(True)
    user2_info = auth_register("ginrou@gmail.com", "zesxdcfghbjn", "Bradley", "Ruler")
    # user1 starts the standup
    standup_start(user1_info["token"], channel_id["channel_id"], 1)
    # error occurs if user2 makes a standup_send since he is not in channel
    with pytest.raises(AccessError) as excinfo:
        standup_send(user2_info["token"], channel_id["channel_id"],
                     "This is the message that is going to be sent to the public channel")
    assert "Authorised user is not a member of the channel" in str(excinfo.value)
    sleep(1)

def test_standup_send_failed_unauthorised_private():
    """ Test to see that a user is not in a channel where the message is within
    This is for when a channel is private
    AccessError occur as ("Attempt to send message to standup channel failed, due to
    user not in current channel")
    """
    func_startup()
    user1_info, channel_id = user_channel_create(False)
    user2_info = auth_register("sennsws@gmail.com", "pillowpet123", "Mai", "Kintarou")
    # user1 starts the standup
    standup_start(user1_info["token"], channel_id["channel_id"], 1)
    # error occurs if user2 makes a standup_send since he is not in channel
    with pytest.raises(AccessError) as excinfo:
        standup_send(user2_info["token"], channel_id["channel_id"],
                     "This is the message that is going to be sent to the private channel")
    assert "Authorised user is not a member of the channel" in str(excinfo.value)
    sleep(1)

def test_standup_send_successful_public_channel():
    """ Test for when standup_send is successful
    This includes for when message is under 1000 characters
    Example: message = "I like to eat eggs for breakfast"
             message = "watermelonisthebest"
             message " "I am clever!!!!"
    This case is for public channels
    """
    func_startup()
    user_info, channel_id = user_channel_create(True)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    standup_send(user_info["token"], channel_id["channel_id"],
                 "I like to eat eggs for breakfast")
    standup_send(user_info["token"], channel_id["channel_id"], "watermelonisthebest")
    standup_send(user_info["token"], channel_id["channel_id"], "I am clever!!!!")
    messages = channel_messages(user_info["token"], channel_id["channel_id"], 0)
    assert messages["messages"] == []
    sleep(1)

def test_standup_send_successful_private_channel():
    """ Test for when standup_send is successful
    This includes for when message is under 1000 characters
    Example: message = "I like long walks"
             message = "keephydrated"
             message = "Confusion!!!!"
    This case is for private channels
    """
    func_startup()
    user_info, channel_id = user_channel_create(False)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    standup_send(user_info["token"], channel_id["channel_id"], "I like long walks")
    standup_send(user_info["token"], channel_id["channel_id"], "keephydrated")
    standup_send(user_info["token"], channel_id["channel_id"], "Confusion!!!!")
    messages = channel_messages(user_info["token"], channel_id["channel_id"], 0)
    assert messages["messages"] == []
    sleep(1)

def test_standup_start_standupexists_public_channel():
    """ Test to see if a standup is already active in the current channel
    Case considers for public
    First user starts the standup, if second user calls standup, error occurs
    Raise a ValueError upon error
    """
    func_startup()
    user1_info, channel_id = user_channel_create(True)
    user2_info = auth_register("lemonade@gmail.com", "trees1234", "Book", "Printer")
    channel_join(user2_info["token"], channel_id["channel_id"])
    standup_start(user1_info["token"], channel_id["channel_id"], 1)
    with pytest.raises(ValueError) as excinfo:
        standup_start(user2_info["token"], channel_id["channel_id"], 1)
    assert "A standup is already active in the current channel" in str(excinfo.value)
    sleep(1)

def test_standup_start_standup_exists_private_channel():
    """ Test to see if a standup is already active in the current channel
    Case considers for private
    First user starts the standup, if second user calls standup, error occurs
    Raise a ValueError upon error
    """
    func_startup()
    user1_info, channel_id = user_channel_create(False)
    user2_info = auth_register("lemonade@gmail.com", "trees1234", "Book", "Printer")
    channel_invite(user1_info["token"], channel_id["channel_id"], user2_info["u_id"])
    standup_start(user1_info["token"], channel_id["channel_id"], 1)
    with pytest.raises(ValueError) as excinfo:
        standup_start(user2_info["token"], channel_id["channel_id"], 1)
    assert "A standup is already active in the current channel" in str(excinfo.value)
    sleep(1)

def test_standup_send_standup_no_exist_public_channel():
    """ Test to see if there is no standup running in the current channel
    This case considers for public channel
    Can't use standup_send when no standup is running
    Raise ValueError upon error
    """
    func_startup()
    user_info, channel_id = user_channel_create(True)
    with pytest.raises(ValueError) as excinfo:
        standup_send(user_info["token"], channel_id["channel_id"],
                     "this is a random message")
    assert "No standup running" in str(excinfo.value)

def test_standup_send_standup_no_exist_private_channel():
    """ Test to see if there is no standup running in the current channel
    This case considers for private channel
    Can't use standup_send when no standup is running
    Raise ValueError upon error
    """
    func_startup()
    user_info, channel_id = user_channel_create(False)
    with pytest.raises(ValueError) as excinfo:
        standup_send(user_info["token"], channel_id["channel_id"],
                     "this is a random message")
    assert "No standup running" in str(excinfo.value)

def test_standup_active_invalid_channel_public():
    """ Test that returns the time that the standup finish. This case deals with calling a
    standup_active when the channel is invalid
    This case tests for when a channel is public
    Raise ValueError upon error
    """
    func_startup()
    user_info, channel_id = user_channel_create(True)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    with pytest.raises(ValueError) as excinfo:
        standup_active(user_info["token"], channel_id["channel_id"] + 13)
    assert "Invalid channel id" in str(excinfo.value)
    sleep(1)

def test_standup_active_invalid_channel_private():
    """ Test that returns the time that the standup finish. This case deals with calling a
    standup_active when the channel is invalid
    This case tests for when a channel is private
    Raise ValueError upon error
    """
    func_startup()
    user_info, channel_id = user_channel_create(False)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    with pytest.raises(ValueError) as excinfo:
        standup_active(user_info["token"], channel_id["channel_id"] + 13)
    assert "Invalid channel id" in str(excinfo.value)
    sleep(1)

def test_standup_active_channel_nostandup():
    """ Test that see if standup_active runs successfully if there is a valid channel but there
    are no standup running in the current channel.
    We create a public/private channel
    """
    func_startup()
    # test for public channel
    user1_info, channel_id = user_channel_create(True)
    active1_info = standup_active(user1_info["token"], channel_id["channel_id"])
    assert not active1_info["is_active"]
    # test for private channel
    user2_info, channel_id = user_channel_create(False)
    active2_info = standup_active(user2_info["token"], channel_id["channel_id"])
    assert not active2_info["is_active"]

def test_standup_active_successful_public_channel():
    """ Test that will return the time after the standup has finished. This case assumes
    that valid standup has already been active.
    This case deals with when the channel is public calls a standup
    """
    func_startup()
    user_info, channel_id = user_channel_create(True)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    active_info = standup_active(user_info["token"], channel_id["channel_id"])
    assert active_info["is_active"]
    sleep(1)

def test_standup_active_successful_private_channel():
    """ Test that will return the time after the standup has finished. This case assumes
    that valid standup has already been active.
    This case deals with when the channel is private calls a standup
    """
    func_startup()
    user_info, channel_id = user_channel_create(False)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    active_info = standup_active(user_info["token"], channel_id["channel_id"])
    assert active_info["is_active"]
    sleep(1)

def test_standup_end_successful_public_channel():
    """ Test that will call standup_end which is a function that saves the messages in a standup
    onto a message queue and removes it once it is done.
    We call this function during standup in a public channel
    """
    func_startup()
    # testing case for public channel
    standup_messages = [
        "apple",
        "banana",
        "carrot",
    ]
    user_info, channel_id = user_channel_create(True)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    for msg in standup_messages:
        standup_send(user_info["token"], channel_id["channel_id"], msg)
    sleep(2)
    messages = channel_messages(user_info["token"], channel_id["channel_id"], 0)
    final_msg = messages["messages"][0]["message"]
    for msg in standup_messages:
        assert msg in final_msg

def test_standup_end_successful_private_channel():
    """ Test that will call standup_end which is a function that saves the messages in a standup
    onto a message queue and removes it once it is done.
    We call this function during standup in a private channel
    """
    func_startup()
    # testing case for private channel
    standup_messages = [
        "chair",
        "table",
        "clock",
    ]
    user_info, channel_id = user_channel_create(False)
    standup_start(user_info["token"], channel_id["channel_id"], 1)
    for msg in standup_messages:
        standup_send(user_info["token"], channel_id["channel_id"], msg)
    sleep(2)
    messages = channel_messages(user_info["token"], channel_id["channel_id"], 0)
    final_msg = messages["messages"][0]["message"]
    for msg in standup_messages:
        assert msg in final_msg
