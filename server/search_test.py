"""Unit test for the search() function.

Designed to be run using the pytest utility.

ASSUMPTION These tests assume that the state of the program is reset after each test.

ASSUMPTION The search function works without any regard to the channel the messages are in.
"""

from server import auth
from server import channel
from server import channels
from server import data
from server import message
from server import search

def test_search_variety():
    """Unit test for execution of the search() function on multiple messages,
       some which match the query and some which do not.

    Creates two users, two channels, and a bunch of test messages from both users.
    Ensures that the right messages are returned.

    The channel that the authorised user is not in should not return any hits.
    """

    auth.reset_auth_data()
    data.initialise_data()
    query_str = "ell"
    message_strings_1 = {
        "Hello!",
        "Nice to meet you.",
        "I fell down the stairs this morning",
        "The death knell rings!",
        "Have you guys finished the 1531 project?",
        "Am I just talking to myself here?",
        "Well, whatever.",
    }
    message_strings_2 = {
        "Tell me guys, is there anyone else here?",
        "Seems like it's just me...",
        "I'm so lonely",
        "Uh.... Bell.",
    }

    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channel_info = channels.channels_create(user_info_1["token"], "my server", 1)

    for message_str in message_strings_1:
        message.message_send(user_info_1["token"], channel_info["channel_id"], message_str)

    auth.auth_logout(user_info_1["token"])
    user_info_2 = auth.auth_register("anotheremail@hotmail.com", "blahblah293", "Wonder", "Woman")
    channel.channel_join(user_info_2["token"], channel_info["channel_id"])

    for message_str in message_strings_2:
        message.message_send(user_info_2["token"], channel_info["channel_id"], message_str)

    search_return = search.search(user_info_2["token"], query_str)
    # Creates a new set of messages that comprises strings that contain query_str
    matching_messages = {msg for msg in (message_strings_1 | message_strings_2) if query_str in msg}
    returned_messages = set()

    for msg in search_return["messages"]:
        returned_messages.add(msg["message"])

    assert returned_messages == matching_messages, "Incorrect search"

def test_search_no_matches():
    """Unit test for execution of the search() function on multiple messages,
       none of which match the query.

    Creates two users, a channel, and a bunch of test messages from both users.
    Ensures that the no messages are returned.
    """

    auth.reset_auth_data()
    data.initialise_data()
    query_str = "grasshopper"
    message_strings_1 = {
        "The lake is a long way from here.",
        "Rock music approaches at high velocity.",
        "The clock within this blog and the clock on my laptop are synchronised",
        "He turned in the research paper on Friday.",
        "A glittering gem is not enough.",
    }
    message_strings_2 = {
        "The shooter says goodbye to his love.",
        "I really want to go to work, but I am too sick to drive.",
        "Writing a list of random sentences is harder than I initially thought it would be.",
        "The river stole the gods.",
    }

    user_info_1 = auth.auth_register("testemail@hotmail.com", "badpassword123", "Captain", "Wonky")
    channel_info = channels.channels_create(user_info_1["token"], "my server", 1)

    for message_str in message_strings_1:
        message.message_send(user_info_1["token"], channel_info["channel_id"], message_str)

    auth.auth_logout(user_info_1["token"])
    user_info_2 = auth.auth_register("anotheremail@hotmail.com", "blahblah293", "Wonder", "Woman")
    channel.channel_join(user_info_2["token"], channel_info["channel_id"])

    for message_str in message_strings_2:
        message.message_send(user_info_2["token"], channel_info["channel_id"], message_str)

    search_return = search.search(user_info_2["token"], query_str)
    assert not search_return["messages"]  # asserts list of messages returned is empty.
