""" Unit tests for all functions implementing the messaging feature. """

import datetime
import time
import pytest

from server import auth
from server import channel
from server import channels
from server import data
from server import message
from server.Error import AccessError, ValueError

def test_message_sendlater_channel_id_not_exist():
    """
    Tests for an invalid channel id when a message is sent.
    test_message_sendlater_channel_id_not_exist()
    E.g. Correct: id = 1, input: id = -1
    Should be thrown ValueError("Invalid channel id")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create a channel
    channels.channels_create(user_info["token"], "channel 1", True)
    with pytest.raises(ValueError) as excinfo:
        date = datetime.datetime(2020, 3, 17)
        message.message_sendlater(user_info["token"], 12312231, "Hello, this is my message!",
                                  int(date.timestamp()))
    assert "Invalid channel id" in str(excinfo.value), "Raised error does not match"

def test_message_sendlater_exceeds_charlimit():
    """
    Tests for if message limit exceeds 1000 characters.
    test_message_sendlater_exceeds_charlimit()
    E.g. "012345789" * 101
    Should be thrown ValueError("Exceed 1000 word limit")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create a channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    #Set the time
    date = datetime.datetime(2020, 3, 17)
    #Set message to 1000 of length
    message1000 = "0123456789"
    message1000 *= 101
    with pytest.raises(ValueError) as excinfo:
        message.message_sendlater(user_info["token"], new_channel["channel_id"], message1000, date)
    assert "Exceed 1000 word limit" in str(excinfo.value), "Raised error does not match"

def test_message_sendlater_past_date():
    """
    Tests for an invalid time when a message is sent.
    test_message_sendlater_past_date()
    E.g. Current: 3/10/19, input: 2/9/18
    Should be thrown ValueError("Time sent is in the past")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create a channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    with pytest.raises(ValueError) as excinfo:
        date = datetime.datetime(2000, 5, 5)
        message.message_sendlater(user_info["token"], new_channel["channel_id"],
                                  "Hello, this is my message!",
                                  int(date.timestamp()))
    assert "Time sent is in the past" in str(excinfo.value), "Raised error does not match"

def test_message_sendlater_invalid_member():
    """
    Tests for if user sending is a valid member
    test_message_sendlater_invalid_member()
    E.g. All User of Channel 1 = [1,2,3,4,5]
    User trying to send later = 6
    Should be thrown AccessError("User is not member of the channel")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info1 = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    user_info2 = auth.auth_register("davidshin@gmail.com", "greatpassword123", "David", "Shin")
    #Create channel 1 and 2
    new_channel1 = channels.channels_create(user_info1["token"], "channel 1", True)
    #new_channel2 = channels.channels_create(user_info2["token"], "channel 1", True)
    date = datetime.datetime.now() + datetime.timedelta(seconds=2)
    with pytest.raises(AccessError) as excinfo:
        message.message_sendlater(user_info2["token"], new_channel1["channel_id"],
                                  "Hello, this is my message!",
                                  int(date.timestamp()))
    assert "User is not member of the channel" in str(excinfo.value), "Raised error does not match"

def test_message_sendlater_success():
    """
    Tests for successful message send later
    test_message_sendlater_success()
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create a channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    message_body = "Hello, this is my message!"
    date = datetime.datetime.now() + datetime.timedelta(seconds=2)
    message.message_sendlater(user_info["token"], new_channel["channel_id"], message_body,
                              int(date.timestamp()))
    time.sleep(3)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["message"] == message_body

def test_message_send_above_message_limit():
    """
    Tests for if message limit exceeds 1000 characters.
    test_message_send_above_message_limit()
    E.g. "012345789" * 101
    Should be thrown ValueError("Exceed 1000 word limit")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    #Set message to length 1000
    message1000 = "0123456789"
    message1000 *= 101
    with pytest.raises(ValueError) as excinfo:
        message.message_send(user_info["token"], new_channel["channel_id"], message1000)
    assert "Exceed 1000 word limit" in str(excinfo.value), "Raised error does not match"

def test_message_send_invalid_channel_id():
    """
    Tests for if channel id received is valid
    test_message_send_invalid_channel_id()
    E.g. Channel id = 1, supplied channel id = 2
    Should be thrown ValueError("Invalid channel id")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    channels.channels_create(user_info["token"], "channel 1", True)
    with pytest.raises(ValueError) as excinfo:
        message.message_send(user_info["token"], 5, "Hello, this is my message!")
    assert "Invalid channel id" in str(excinfo.value), "Raised error does not match"

def test_message_send_invalid_member():
    """
    Tests for if sender is a valid member of the channel.
    test_message_send_invalid_member()
    E.g. Members = [1,2,3,4,5], sender id = 6
    Should be thrown AccessError("User is not member of the channel")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info1 = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    user_info2 = auth.auth_register("davidshin@gmail.com", "greatpassword123", "David", "Shin")
    #Create new channel
    new_channel1 = channels.channels_create(user_info1["token"], "channel 1", True)
    #new_channel2 = channels.channels_create(user_info2["token"], "channel 1", True)
    with pytest.raises(AccessError) as excinfo:
        message.message_send(user_info2["token"], new_channel1["channel_id"],
                             "Hello, this is my message!")
    assert "User is not member of the channel" in str(excinfo.value), "Raised error does not match"

def test_message_send_success():
    """
    Tests for successful message send
    test_message_send_success()
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    message_body = "Hello, this is my message!"
    message.message_send(user_info["token"], new_channel["channel_id"], message_body)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["message"] == message_body

def test_message_remove_invalid_message_id():
    """
    Test whether the message_id of the message exist
    test_message_remove_invalid_message_id()
    E.g message_id[0,1,2,3,4] - message_remove("12345", 5)
    Should be thrown ValueError("Invalid message id")

    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create a channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    #Create new message
    message.message_send(user_info["token"], new_channel["channel_id"], "Hello this a message")
    with pytest.raises(ValueError) as excinfo:
        message.message_remove(user_info["token"], 3)
    assert "Invalid message id" in str(excinfo.value), "Raised error does not match"

def test_message_remove_invalid_poster_edit():
    """
    Test that the user is trying to edit is not the poster of the message
    test_message_remove_invalid_poster_edit()
    E.g poster = "12345" user = "67890"
    Should be thrown AccessError("User does not have permission")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    user2_info = auth.auth_register("davidshin@gmail.com", "greatpassword123", "David", "Shin")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    with pytest.raises(AccessError) as excinfo:
        message.message_remove(user2_info["token"], message_id["message_id"])
    assert "User does not have permission" in str(excinfo.value), "Raised error does not match"

def test_message_remove_success():
    """
    Test for successful removing of message
    test_message_remove_success()
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create a channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    channel.channel_messages(user1_info["token"], new_channel["channel_id"], 0)
    message.message_remove(user1_info["token"], message_id["message_id"])
    with pytest.raises(ValueError) as excinfo:
        message.message_remove(user1_info["token"], message_id["message_id"])
    assert "Invalid message id" in str(excinfo.value)

def test_message_edit_above_message_limit():
    """
    Tests for if message limit exceeds 1000 characters.
    test_message_edit_above_message_limit()
    E.g. "012345789" * 101
    Should be thrown ValueError("Exceed 1000 word limit")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    #Create a new valid message:
    message_id = message.message_send(user_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    #Set message length to 1000 length
    message1000 = "0123456789"
    message1000 *= 101
    with pytest.raises(ValueError) as excinfo:
        message.message_edit(user_info["token"], message_id["message_id"], message1000)
    assert "Exceed 1000 word limit" in str(excinfo.value), "Raised error does not match"

def test_message_edit_invalid_message_id():
    """Test whether the message_id exist when removing

    message_remove_invalid_message_id_test()
    E.g message_id[0,1,2,3,4] - message_remove("12345", 5)
    Should be thrown ValueError("Invalid message id")

    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    #Create a message
    message.message_send(user_info["token"], new_channel["channel_id"], "Hello this a message")
    with pytest.raises(ValueError) as excinfo:
        message.message_edit(user_info["token"], 5, "Hello this a NEW message")
    assert "Invalid message id" in str(excinfo.value), "Raised error does not match"

def test_message_edit_invalid_editor():
    """
    Test that the message is edited not by the poster
    test_message_edit_invalid_editor()
    E.g Token = "12345" editor = "67890"
    Should be thrown a AccessError("User does not have permission")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    user2_info = auth.auth_register("davidshin@gmail.com", "greatpassword123", "David", "Shin")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    with pytest.raises(AccessError) as excinfo:
        message.message_edit(user2_info["token"], message_id["message_id"],
                             "Here is the new message!")
    assert "User does not have permission" in str(excinfo.value), "Raised error does not match"

def test_message_edit_success():
    """
    Test that message can be succesfully edited
    test_message_edit_success()
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    message_body = "Hello, this is my message!"
    message_edit_body = "This is my new message!"
    message.message_send(user_info["token"], new_channel["channel_id"], message_body)
    message.message_edit(user_info["token"], new_channel["channel_id"], message_edit_body)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["message"] == message_edit_body

def test_message_edit_success_empty():
    """
    Test that message can be succesfully edited
    test_message_edit_success()
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    message_body = "Hello, this is my message!"
    message.message_send(user_info["token"], new_channel["channel_id"], message_body)
    message.message_edit(user_info["token"], new_channel["channel_id"], "")
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"] == []

def test_message_react_invalid_message_id():
    """
    Test the message_id does not exist when react
    test_message_react_invalid_message_id()
    E.g message_id[0,1,2,3,4] - message_react("12345", -1, 3)
    Should be thrown ValueError("Invalid message id")

    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message.message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                              "Hello this a message")
    with pytest.raises(ValueError) as excinfo:
        message.message_react(user1_info["token"], 3, 1)
    assert "Invalid message id" in str(excinfo.value), "Raised error does not match"

def test_message_react_invalid_react_id():
    """
    Test the react_id does not exist when react
    test_message_react_invalid_react_id()
    E.g react_ID = -1
    Should be thrown ValueError("Invalid react id")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    #message.message_react(user1_info["token"], message_id["message_id"], 1)
    #message.message_unreact(user1_info["token"], message_id["message_id"], 1)
    with pytest.raises(ValueError) as excinfo:
        message.message_react(user1_info["token"], message_id["message_id"], 15)
    assert "Invalid react id" in str(excinfo.value), "Raised error does not match"

def test_message_react_active_react_id():
    """
    Test unreacting an non active react id
    test_message_react_active_react_id()
    E.g react_ID = 1
    Should be thrown ValueError("React Id already not active")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    # make a channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    message.message_react(user1_info["token"], message_id["message_id"], 1)
    with pytest.raises(ValueError) as excinfo:
        message.message_react(user1_info["token"], message_id["message_id"], 1)
    assert "React Id already active" in str(excinfo.value), "Raised error does not match"

def test_message_react_success(): #TEST
    """
    Test that a message can be successfully reacted
    test_message_react_success()
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    message_body = "test message body here"
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    message_id = message.message_send(user_info["token"], new_channel["channel_id"], message_body)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["message"] == message_body
    message.message_react(user_info["token"], message_id["message_id"], 1)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["reacts"][0]["react_id"] == 1

def test_message_unreact_invalid_message_id():
    """
    Test if message_id does not exist when react is called
    test_message_unreact_invalid_message_id()
    E.g message_id[0,1,2,3,4] - message_unreact("12345", -1, 3)
    Should be thrown ValueError("Invalid message id")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message.message_send(user1_info["token"], new_channel["channel_id"], "Hello this a message")
    with pytest.raises(ValueError) as excinfo:
        message.message_unreact(user1_info["token"], 2, 3)
    assert "Invalid message id" in str(excinfo.value), "Raised error does not match"

def test_message_unreact_invalid_react_id():
    """
    Test the react_id does not exist when react
    test_message_unreact_invalid_react_id()
    E.g react_ID = -1
    Should be thrown ValueError("Invalid react id")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    with pytest.raises(ValueError) as excinfo:
        message.message_unreact(user1_info["token"], message_id["message_id"], 15)
    assert "Invalid react id" in str(excinfo.value), "Raised error does not match"

def test_message_unreact_non_active_react_id():
    """
    Test unreacting an non active react id
    test_message_unreact_non_active_react_id
    E.g react_ID = 1
    Should be thrown ValueError("React Id already not active")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    with pytest.raises(ValueError) as excinfo:
        message.message_unreact(user1_info["token"], message_id["message_id"], 1)
    assert "React Id already not active" in str(excinfo.value), "Raised error does not match"

def test_message_unreact_success(): #TEST
    """
    Test that a message can be successfully unreacted
    test_message_unreact_success()
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    message_body = "test message body here"
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    message_id = message.message_send(user_info["token"], new_channel["channel_id"], message_body)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["message"] == message_body
    message.message_react(user_info["token"], message_id["message_id"], 1)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["reacts"][0]["react_id"] == 1
    message.message_unreact(user_info["token"], message_id["message_id"], 1)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["reacts"] == []

def test_message_pin_invalid_message_id():
    """Test the message_id does not exist when pin
    test_message_pin_invalid_message_id()
    E.g message_id[0,1,2,3,4] - message_pin("12345", 6, 3)
    Should be thrown ValueError("Invalid message id")

    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message.message_send(user1_info["token"],
                         new_channel["channel_id"],
                         "Hello this a message")
    with pytest.raises(ValueError) as excinfo:
        message.message_pin(user1_info["token"], 6)
    assert "Invalid message id" in str(excinfo.value), "Raised error does not match"

def test_message_pin_invalid_user_permission():
    """
    Test that the message is edited not by the poster
    test_message_pin_invalid_user_permission()
    E.g Token = "12345" editor = "67890"
    Should be thrown a AccessError("User does not have permission")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    user2_info = auth.auth_register("davidshin@gmail.com", "greatpassword123", "David", "Shin")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    with pytest.raises(AccessError) as excinfo:
        message.message_pin(user2_info["token"], message_id["message_id"])
    assert "User does not have permission" in str(excinfo.value), "Raised error does not match"

def test_message_pin_already():
    """
    Test the message with ID message_id is already pinned
    test_message_pin_already()
    E.g current pinned id = 3, pin request = 3
    Should be thrown ValueError("Message already pinned")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    message.message_pin(user1_info["token"], message_id["message_id"])
    #message.message_unpin(user1_info["token"], message_id["message_id"])
    #message.message_pin(user1_info["token"], message_id["message_id"])
    with pytest.raises(ValueError) as excinfo:
        message.message_pin(user1_info["token"], message_id["message_id"])
    assert "Message is already pinned" in str(excinfo.value), "Raised error does not match"

def test_message_pin_success(): #TEST
    """
    Test that a message can be successfully pinned
    test_message_pin_success()
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    message_body = "test message body here"
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    message_id = message.message_send(user_info["token"], new_channel["channel_id"], message_body)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["message"] == message_body
    message.message_pin(user_info["token"], message_id["message_id"])
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["is_pinned"]

def test_message_unpin_invalid_user_permission():
    """
    Test that the message is edited not by the poster
    test_message_pin_invalid_user_permission()
    E.g Token = "12345" editor = "67890"
    Should be thrown a AccessError("User does not have permission")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    user2_info = auth.auth_register("davidshin@gmail.com", "greatpassword123", "David", "Shin")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    with pytest.raises(AccessError) as excinfo:
        message.message_unpin(user2_info["token"], message_id["message_id"])
    assert "User does not have permission" in str(excinfo.value), "Raised error does not match"

def test_message_unpin_invalid_message_id():
    """
    Test the message_id does not exist when unpin
    test_message_unpin_invalid_message_id()
    E.g message_id[0,1,2,3,4] - message_unpin("12345", 6, 3)

    Should be thrown ValueError("Invalid message id")

    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message.message_send(user1_info["token"], new_channel["channel_id"], "Hello this a message")
    with pytest.raises(ValueError) as excinfo:
        message.message_unpin(user1_info["token"], 6)
    assert "Invalid message id" in str(excinfo.value), "Raised error does not match"

def test_message_unpin_inactive_pin():
    """
    Test the message with ID message_id is already unpinned
    test_message_unpin_inactive_pin()
    E.g current pinned id = 2, unpin request = 3
    Should be thrown ValueError("Message already unpinned")
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user1_info["token"], "channel 1", True)
    #Create a message
    message_id = message.message_send(user1_info["token"], new_channel["channel_id"],
                                      "Hello this a message")
    with pytest.raises(ValueError) as excinfo:
        message.message_unpin(user1_info["token"], message_id["message_id"])
    assert "Message is already unpinned" in str(excinfo.value), "Raised error does not match"

def test_message_unpin_success(): #TEST
    """
    Test that a message can be successfully unpinned
    test_message_unpin_success()
    """
    #Register User
    auth.reset_auth_data()
    data.initialise_data()
    message_body = "test message body here"
    user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    #Create new channel
    new_channel = channels.channels_create(user_info["token"], "channel 1", True)
    message_id = message.message_send(user_info["token"], new_channel["channel_id"], message_body)
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["message"] == message_body
    message.message_pin(user_info["token"], message_id["message_id"])
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert messages["messages"][0]["is_pinned"]
    message.message_unpin(user_info["token"], message_id["message_id"])
    messages = channel.channel_messages(user_info["token"], new_channel["channel_id"], 0)
    assert not messages["messages"][0]["is_pinned"]
