""" Unit tests for functions implementing features related to a specific channel. """

import pytest
from server import auth
from server import channel
from server import channels
from server import data
from server import message
from server.Error import AccessError, ValueError

def test_channel_invite_unauthorised_user():
    """Tests for an invalid channel id when giving channel invites.

    An invalid channel id can be one that the user is not a member of.

    This test creates three users. One creates a private channel.
    The second attempts to invite the third user to this channel, without being
    a member of that channel.

    Should be thrown ValueError("Cannot invite to invalid channel")
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channel_info = channels.channels_create(user_info_1["token"], "1's private server", 0)
    user_info_3 = auth.auth_register("anotheremail@hotmail.com", "blahblah293", "Wonder", "Woman")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    with pytest.raises(AccessError) as excinfo:
        channel.channel_invite(user_info_2["token"], channel_info["channel_id"],
                               user_info_3["u_id"])
    assert "Authorised user is not a member of the channel" in str(excinfo.value)

def test_channel_invite_invalid_u_id():
    """Tests for an invalid u_id when giving channel invites.

    Registers a user, then that user creates a private channel.
    That user then attempts to add an invalid u_id to the new channel.

    Should be thrown ValueError("Invalid u_id")
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channel_info = channels.channels_create(user_info_1["token"], "1's private server", 0)
    with pytest.raises(ValueError) as excinfo:
        channel.channel_invite(user_info_1["token"], channel_info["channel_id"], 542353)
    assert "Invalid user id" in str(excinfo.value)

def test_channel_invite_channel_dne():
    """ Test that checks whether you can invite another user into a channel.
    Must require 2 valid users (register them), where one user creates the channel and invites
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channels.channels_create(user_info_1["token"], "1's private server", 0)
    with pytest.raises(ValueError) as excinfo:
        channel.channel_invite(user_info_1["token"], 321321, user_info_2["u_id"])
    assert "Invalid channel id" in str(excinfo.value)

def test_channel_invite_already_member():
    """ Test that checks whether the user is a number of the current channel.
    If the user isn't, then raise ValueError when you invite them to channel.
    Must require 2 users to register, where one user creates a channel.
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], "1's private server", 1)
    channel.channel_join(user_info_2["token"], channel_info["channel_id"])
    with pytest.raises(ValueError) as excinfo:
        channel.channel_invite(user_info_1["token"], channel_info["channel_id"],
                               user_info_2["u_id"])
    assert "Invited user is already a member of the channel" in str(excinfo.value)

def test_channel_invite_successful():
    """Tests a successful channel invite scenario.

    When a user is invited, they are automatically a member of that channel.
    Asserts that the invited user has been added to the channel by making sure
    that the new channel is in the list of channels that they are in.
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channel_info = channels.channels_create(user_info_1["token"], "1's private server", 0)
    channel.channel_invite(user_info_1["token"], channel_info["channel_id"], user_info_2["u_id"])
    user_2_channels = channels.channels_list(user_info_2["token"])

    is_in_new_channel = False
    for i in user_2_channels["channels"]:
        if channel_info["channel_id"] == i["channel_id"]:
            is_in_new_channel = True

    assert is_in_new_channel, "Invited user is not a member of the channel"

def test_channel_details_channel_dne():
    """Tests for an invalid (non-existent) channel id when checking channel details.

    Should be thrown ValueError("Channel does not exist")
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    with pytest.raises(ValueError) as excinfo:
        channel.channel_details(user_info["token"], 12213)
    assert "Invalid channel id" in str(excinfo.value)

def test_channel_details_not_channel_member():
    """Tests for a user accessing details of a channel they are not a member of.

    Should be thrown AccessError("Not a member of this channel")
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channel_info = channels.channels_create(user_info_1["token"], "1's private server", 0)
    with pytest.raises(AccessError) as excinfo:
        channel.channel_details(user_info_2["token"], channel_info["channel_id"])
    assert "Authorised user is not a member of the channel" in str(excinfo.value)

def test_channel_details_successful():
    """Tests for a successful channel_detail() call.
    Asserts that the right data is returned when it is called.
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's private server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 0)
    channel.channel_invite(user_info_1["token"], channel_info["channel_id"], user_info_2["u_id"])
    channel_details_dict = channel.channel_details(user_info_1["token"], channel_info["channel_id"])

    assert channel_details_dict["name"] == channel_name
    assert user_info_1["u_id"] == channel_details_dict["owner_members"][0]["u_id"]
    member_u_id_list = [member["u_id"] for member in channel_details_dict["all_members"]]
    assert user_info_1["u_id"] and user_info_2["u_id"] in member_u_id_list

def test_channel_messages_channel_dne():
    """ Tests for trying to message a channel that does not exist
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    with pytest.raises(ValueError) as excinfo:
        channel.channel_messages(user_info_1["token"], 123, 456)
    assert "Invalid channel id" in str(excinfo.value)

def test_channel_messages_start_too_big():
    """ Channel_messages_start_too_big_test()
    Tests for start being larger than the number of messages in channel
    Should be thrown ValueError("Start is larger than the number of messages")
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 0)
    with pytest.raises(ValueError) as excinfo:
        channel.channel_messages(user_info_1["token"], channel_info["channel_id"], 456)
    assert ("Start index of message page exceeds number of messages in the channel" in
            str(excinfo.value))

def test_channel_messages_not_channel_member():
    """ Channel_messages_not_channel_member_test()
    Tests for user not being a member of this channel
    Should be thrown AccessError("Not a member of this channel")
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 0)
    with pytest.raises(AccessError) as excinfo:
        channel.channel_messages(user_info_2["token"], channel_info["channel_id"], 456)
    assert "Authorised user is not a member of the channel" in str(excinfo.value)

def test_channel_messages_success():
    """ Tests for successfull use of channel_messages
    Must include msg funcitons
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    #user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 0)
    #channel.channel_join(user_info_1["token"], 123)
    message.message_send(user_info_1["token"], channel_info["channel_id"], "Words")
    received = channel.channel_messages(user_info_1["token"], channel_info["channel_id"], 0)
    assert received["messages"][0]["message"] == "Words"
    assert received["end"] == -1

def test_channel_messages_success_long():
    """ Tests for successfull use of channel_messages
    Must include msg funcitons
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    #user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 0)
    #channel.channel_join(user_info_1["token"], 123)
    for i in range(100):
        message.message_send(user_info_1["token"], channel_info["channel_id"], f"message {i}")
    received = channel.channel_messages(user_info_1["token"], channel_info["channel_id"], 0)
    for i in range(50):
        assert received["messages"][i]["message"] == f"message {99 - i}"
    received = channel.channel_messages(user_info_1["token"], channel_info["channel_id"],
                                        received["end"])
    print(received["start"], ",", received["end"])
    for i in range(50):
        assert received["messages"][i]["message"] == f"message {49 - i}"
    channel.channel_messages(user_info_1["token"], channel_info["channel_id"],
                                        received["end"])

def test_channel_leave_channel_dne():
    """ Channel_leave_channel_dne_test()
    Tests for channel being left not existing
    Should be thrown ValueError("Channel does not exist")
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    with pytest.raises(ValueError) as excinfo:
        channel.channel_leave(user_info_1["token"], 123)
    assert "Invalid channel id" in str(excinfo.value)

def test_channel_leave_success():
    """ Channel_leave_success_test()
    Tests for channel being left successfully
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 1)
    channel.channel_join(user_info_2["token"], channel_info["channel_id"])
    user_2_channels = channels.channels_list(user_info_2["token"])

    is_in_new_channel = False

    for i in user_2_channels["channels"]:
        if channel_info["channel_id"] == i["channel_id"]:
            is_in_new_channel = True
    channel.channel_leave(user_info_2["token"], channel_info["channel_id"])
    left_channel = False
    if is_in_new_channel is True:
        left_channel = True
    assert left_channel, "User left channel"

def test_channel_join_channel_dne():
    """ Channel_join_channel_dne_test()
    Tests for channel being joined not existing
    Should be thrown ValueError("Channel does not exist")
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    with pytest.raises(ValueError) as excinfo:
        channel.channel_join(user_info_1["token"], 123)
    assert "Invalid channel id" in str(excinfo.value)

def test_channel_join_private_channel():
    """ Channel_join_private_channel_test()
    Tests for channel being joined that is private
    Should be thrown AccessError("Channel is private")
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 0)
    with pytest.raises(AccessError) as excinfo:
        channel.channel_join(user_info_2["token"], channel_info["channel_id"])
    assert "Cannot join private channel with regular user permissions." in str(excinfo.value)

def test_channel_join_already_member():
    """ Test to check whether a user is already a member of the channel.
    If the user is, then raise ValueError when they try to join the channel.
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], "1's private server", 1)
    channel.channel_join(user_info_2["token"], channel_info["channel_id"])
    with pytest.raises(ValueError) as excinfo:
        channel.channel_join(user_info_2["token"], channel_info["channel_id"])
    assert "User is already a member of the channel" in str(excinfo.value)

def test_channel_join_success():
    """ Channel_join_success_test()
    Tests for channel succesfully being joined
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 1)
    channel.channel_join(user_info_2["token"], channel_info["channel_id"])
    user_2_channels = channels.channels_list(user_info_2["token"])
    for i in user_2_channels["channels"]:
        if channel_info["channel_id"] == i["channel_id"]:
            is_in_new_channel = True

    assert is_in_new_channel, "User joined channel"

def test_channel_addowner_channel_dne():
    """ Channel_addowner_channel_dne_test()
    Tests for channel adding owner to DNE
    Should be thrown ValueError("Channel does not exist")
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    with pytest.raises(ValueError) as excinfo:
        channel.channel_addowner(user_info_1["token"], 123, user_info_1["u_id"])
    assert "Invalid channel id" in str(excinfo.value)

def test_channel_addowner_already_owner():
    """ Channel_addowner_already_owner_test()
    Tests for adding owner to channel they own
    Should be thrown ValueError("Already an owner")
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 0)
    with pytest.raises(ValueError) as excinfo:
        channel.channel_addowner(user_info_1["token"], channel_info["channel_id"],
                                 user_info_1["u_id"])
    assert "User is already owner of the channel" in str(excinfo.value)

def test_channel_addowner_not_authorised():
    """ Channel_addowner_not_authorised_test()
    Tests for user not being a valid owner of the channel
    Should be thrown AccessError("Unauthorised owner")
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    user_info_3 = auth.auth_register("person@gmail.com", "ilovedogs123", "Real", "Person")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 0)
    with pytest.raises(AccessError) as excinfo:
        channel.channel_addowner(user_info_2["token"], channel_info["channel_id"],
                                 user_info_3["u_id"])
    assert "Authorised user is not a owner of the channel or a Slackr owner" in str(excinfo.value)

def test_channel_addowner_successful():
    """ Channel_addowner_successful_test()
    Tests for succcessful addition of owner to channel
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 0)
    channel.channel_addowner(user_info_1["token"], channel_info["channel_id"], user_info_2["u_id"])
    channel_details_dict = channel.channel_details(user_info_1["token"], channel_info["channel_id"])
    assert channel_details_dict["name"] == channel_name
    assert user_info_1["u_id"] == channel_details_dict["owner_members"][0]["u_id"]
    owner_u_id_list = [owner["u_id"] for owner in channel_details_dict["owner_members"]]
    assert user_info_1["u_id"] in owner_u_id_list and user_info_2["u_id"] in owner_u_id_list

def test_channel_removeowner_channel_dne():
    """ Channel_removeowner_channel_dne_test()
    Tests for channel not existing
    Should be thrown ValueError("Channel does not exist")
    """
    auth.reset_auth_data()
    data.initialise_data()
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    with pytest.raises(ValueError) as excinfo:
        channel.channel_removeowner(user_info_1["token"], 123, user_info_2["u_id"])
    assert "Invalid channel id" in str(excinfo.value)

def test_channel_removeowner_not_owner():
    """ Channel_removeowner_not_owner_test()
    Tests for user removing owner not being an owner
    Should be thrown ValueError("Existing user not an owner")
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channels.channels_create(user_info_1["token"], channel_name, 0)
    with pytest.raises(ValueError) as excinfo:
        channel.channel_removeowner(user_info_2["token"], 123, user_info_1["u_id"])
    assert "Invalid channel id" in str(excinfo.value)

def test_channel_removeowner_not_admin():
    """ Channel_removeowner_not_admin_test()
    Tests for authorised user (admin) not being an owner of the slackr or owner of channel
    Should be thrown ValueError("Not admin")
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channels.channels_create(user_info_1["token"], channel_name, 0)
    with pytest.raises(AccessError) as excinfo:
        channel.channel_removeowner(user_info_2["token"], 1, user_info_1["u_id"])
    assert "Authorised user is not a owner of the channel or a Slackr owner" in str(excinfo.value)

def test_channel_removeowner_subject_not_owner():
    """ Test that checks if the user who created the channel are able to remove another owner
    from the channel.
    Must require 2 users that are registered.
    Raise ValueError when we try remove a member who is not an owner of the channel.
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 1)
    channel.channel_join(user_info_2["token"], channel_info["channel_id"])
    with pytest.raises(ValueError) as excinfo:
        channel.channel_removeowner(user_info_1["token"], 1, user_info_2["u_id"])
    assert "User is not an owner of the channel" in str(excinfo.value)

def test_channel_removeowner_successful():
    """ Test that checks if we are able to remove an owner from a channel.
    Must require 2 users that are registered and are both owners of the channel.
    Assumes that the channel id is valid.
    """
    auth.reset_auth_data()
    data.initialise_data()
    channel_name = "1's server"
    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    user_info_2 = auth.auth_register("spykids@gmail.com", "ilovecats123", "John", "Snow")
    channel_info = channels.channels_create(user_info_1["token"], channel_name, 1)
    channel.channel_join(user_info_2["token"], channel_info["channel_id"])
    channel.channel_addowner(user_info_1["token"], 1, user_info_2["u_id"])
    channel.channel_removeowner(user_info_1["token"], 1, user_info_2["u_id"])
    channel_details = channel.channel_details(user_info_1["token"], channel_info["channel_id"])
    assert user_info_2["u_id"] != channel_details["owner_members"][0]["u_id"]
