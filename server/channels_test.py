""" Unit tests for functions implementing features related to a non-specific channel(s). """

import pytest
from server import auth
from server import channels
from server import data
from server.Error import AccessError, ValueError

def test_channel_list_invalid_token():
    """ Test to see if whether we can see a list of all the channels that the user is part of.
    AccessError is raised when we pass in an invalid token.
    """
    auth.reset_auth_data()
    data.initialise_data()

    user_info = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    with pytest.raises(AccessError) as excinfo:
        channels.channels_list(user_info["token"] + "gibberish")
    assert "Invalid token" in str(excinfo.value), "Raised error does not match"

def test_channel_list_successful():
    """ Test to check if we can see a list of all the channels that the authorised user is
    part of.
    Must require to register some users, also they are required to create a channel.
    The token must be valid.
    """
    auth.reset_auth_data()
    data.initialise_data()

    channel_names = [
        "public test channel",
        "private test channel",
    ]
    user3_channel_name = "user 3's channel"
    user1_info = auth.auth_register("mrbean@gmail.com", "validpassword123", "Mr", "Bean")
    channels.channels_create(user1_info["token"], "public test channel", True)
    user2_info = auth.auth_register("halloween@gmail.com", "cows5320", "Jessica", "Lee")
    channels.channels_create(user2_info["token"], "private test channel", False)
    user3_info = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channels.channels_create(user3_info["token"], user3_channel_name, False)
    channels_info = channels.channels_list(user3_info["token"])
    for channel_info in channels_info["channels"]:
        assert channel_info["name"] not in channel_names
        assert channel_info["name"] == user3_channel_name

def test_channels_listall_invalid_token():
    """ Test to check whether we can see a list of all the channels.
    The user does not have to be part of the channel to see it.
    Raise AccessError if we pass in an invalid token.
    """
    auth.reset_auth_data()
    data.initialise_data()

    user_info = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    with pytest.raises(AccessError) as excinfo:
        channels.channels_listall(user_info["token"] + "gibberish")
    assert "Invalid token" in str(excinfo.value), "Raised error does not match"

def test_channels_listall_successful():
    """ Test that will provide a list of all the channels.
    The user does not need to be part of the channel to see the list.
    Assume that the token is valid.
    """
    auth.reset_auth_data()
    data.initialise_data()

    channel_names = [
        "public test channel",
        "private test channel",
    ]
    user1_info = auth.auth_register("mrbean@gmail.com", "validpassword123", "Mr", "Bean")
    channels.channels_create(user1_info["token"], "public test channel", True)
    user2_info = auth.auth_register("halloween@gmail.com", "cows5320", "Jessica", "Lee")
    channels.channels_create(user2_info["token"], "private test channel", False)
    user3_info = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channels_info = channels.channels_listall(user3_info["token"])
    for channel_info in channels_info["channels"]:
        assert channel_info["name"] in channel_names

def test_channels_create_invalid_token():
    """ Test to see if a channel can be created.
    Requires a user to register before creating the channel.
    Raise an AccessError if the token is invalid.
    """
    auth.reset_auth_data()
    data.initialise_data()

    user_info = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    with pytest.raises(AccessError) as excinfo:
        channels.channels_create(user_info["token"] + "gibberish", "test channel", False)
    assert "Invalid token" in str(excinfo.value), "Raised error does not match"

def test_channels_create_invalid_name():
    """ Test to see if a channel can be create.
    Requires a user to register before creating the channel.
    Assumes that the token is valid.
    Raise a ValueError when we input a channel name longer than 20 characters.
    """
    auth.reset_auth_data()
    data.initialise_data()

    user_info = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    with pytest.raises(ValueError) as excinfo:
        channels.channels_create(user_info["token"],
                                 "Toomanycharachtersinthischannelnamebecausereasons", False)
    assert "Invalid channel name" in str(excinfo.value), "Raised error does not match"

def test_channels_create_successful():
    """ Test to check if a channel can be created.
    Assumes that the token and the channel name is valid.
    Requires the user to register before creating the channel.
    """

    auth.reset_auth_data()
    data.initialise_data()

    user_info = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channels.channels_create(user_info["token"], "test channel", True)
    channels_info = channels.channels_listall(user_info["token"])
    assert channels_info["channels"][0]["name"] == "test channel"
