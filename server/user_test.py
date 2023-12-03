""" Unit tests for functions implementing features related to individual users. """

import pytest
from server import data
from server.user import user_profile, user_profile_setname, user_profile_setemail
from server.user import user_profile_sethandle, user_profiles_uploadphoto
from server.auth import auth_register, reset_auth_data
from server.Error import ValueError

def func_startup():
    """ Resets all the data and the reinitialises it again
    """
    reset_auth_data()
    data.initialise_data()

def test_user_profile_unsuccessful_u_id():
    """Tests for valid information provided by user.

    User providing u_id considered to be invalid.
    ValueError raised when u_id represents user ("Invalid user id")
    This case deals with account that is registered
    """

    func_startup()
    user_info = auth_register("coolkid@gmail.com", "12345qwe", "bob", "smith")
    with pytest.raises(ValueError) as excinfo:
        # Calls user_profile() with Invalid user id
        user_profile(user_info["token"], user_info["u_id"] + 1)
    assert "Invalid user id" in str(excinfo.value)

def test_user_profile_successful():
    """Tests that runs with valid information given
    """

    func_startup()
    user_info = auth_register("coolkid@gmail.com", "12345qwe", "bob", "smith")
    profile_info = user_profile(user_info["token"], user_info["u_id"])
    # checks if there is a string in the user's given information
    assert profile_info["email"] == "coolkid@gmail.com"
    assert profile_info["name_first"] == "bob"
    assert profile_info["name_last"] == "smith"


def test_user_profile_setname_unsuccessful_firstname():
    """Test if first name is invalid (more than 50 characters)

    Example: first_name = "This is a random string that I will be using for pytest"
    ValueError raised upon invalid first name ("Invalid first name has been inputed")
    """

    func_startup()
    user_info = auth_register("flyingtuna@gmail.com", "iloveapple", "peter", "pan")
    profile_info = user_profile(user_info["token"], user_info["u_id"])
    with pytest.raises(ValueError) as excinfo:
        user_profile_setname(user_info["token"], profile_info["name_first"] +
                             "This is a random string that I will be using for pytest",
                             profile_info["name_last"])
    assert "Invalid first name" in str(excinfo.value)

def test_user_profile_setname_unsuccessful_lastname():
    """Test if last name is invalid (more than 50 characters)

    Example: last_name = "I like to eat a lot of vegetables for lunch and dinner"
    ValueError raised upon invalid last name ("Invalid last name has been inserted")
    """

    func_startup()
    user_info = auth_register("yellowracecar@gmail.com", "birthdayboy", "russell", "lee")
    profile_info = user_profile(user_info["token"], user_info["u_id"])
    with pytest.raises(ValueError) as excinfo:
        user_profile_setname(user_info["token"], profile_info["name_first"],
                             profile_info["name_last"] +
                             "I like to eat a lot of vegetables for lunch and dinner")
    assert "Invalid last name" in str(excinfo.value)

def test_user_profile_setname_successful():
    """Tests for if the user enters valid details for first name and last name
       (less than 50 characters)

    Check if the first and last name registered matches with the one set
    Example: first name = "James"
             last name = "Johnson"
    """

    func_startup()
    user_info = auth_register("hotwheels@gmail.com", "password824", "Captain", "Jacob")
    first_name = "Michael"
    last_name = "Jackson"
    user_profile_setname(user_info["token"], first_name, last_name)
    profile_info = user_profile(user_info["token"], user_info["u_id"])
    assert profile_info["name_first"] == first_name
    assert profile_info["name_last"] == last_name


def test_user_profile_setemail_invalid_email():
    """Test if the email setup is invalid.

    Example: email = ringo@gmail or email = ringo@com or email = ringo.com or
             email = ringo.gmail.com or email = ringo.gmail or email = ringo
    ValueError occurs as ("Set email attempted with invalid email")
    """
    func_startup()
    user_info = auth_register("daoko@gmail.com", "goodday44", "Michael", "Jackson")
    with pytest.raises(ValueError) as excinfo:
        user_profile_setemail(user_info["token"], "daoko@gmail")
    assert "Invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        user_profile_setemail(user_info["token"], "daoko@com")
    assert "Invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        user_profile_setemail(user_info["token"], "daoko.com")
    assert "Invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        user_profile_setemail(user_info["token"], "daoko.gmail.com")
    assert "Invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        user_profile_setemail(user_info["token"], "daoko.gmail")
    assert "Invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        user_profile_setemail(user_info["token"], "daoko")
    assert "Invalid email" in str(excinfo.value)

def test_user_profile_setemail_existing_email():
    """Test to see if the email entered has already been used by another user

    Upon error, ValueError will be shown has ("The entered email currently exists")
    """

    func_startup()
    user1_info = auth_register("carrotcake@gmail.com", "lightanddark12471", "Catherine", "Leung")
    user2_info = auth_register("keyboardking@gmail.com", "saberpopsicle321", "Jennifer", "Chan")
    with pytest.raises(ValueError) as excinfo:
        user_profile_setemail(user1_info["token"], "keyboardking@gmail.com")
    assert "Set email attempted with invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        user_profile_setemail(user2_info["token"], "carrotcake@gmail.com")
    assert "Set email attempted with invalid email" in str(excinfo.value)

def test_user_profile_setemail_successful():
    """Tests for when the email is valid to be used, that is, when no existing user has
       occupied the email
    """

    func_startup()
    user_info = auth_register("milkway@gmail.com", "123456qwe", "Paper", "Cut")
    new_email = "spiderman@gmail.com"
    user_profile_setemail(user_info["token"], new_email)
    profile_user_info = user_profile(user_info["token"], user_info["u_id"])
    assert profile_user_info["email"] == new_email

def test_user_profile_sethandle_invalid_handle():
    """Tests to check for when a user profile has an invalid display name
       (more than 20 characters) The cases includes different methods of inputting the
       display name.

    Example: display_name: "Printing out a textbook"  (with spaces)
             display_name: "HappyNewYearEveryone44"   (no spaces)
             display_name: "I don't know!!,,%%&&12"   (with special characters)
    ValueError will occur upon error as ("Display name inserted is invalid due to being
    more than 20 characters")
    """

    func_startup()
    user_info = auth_register("dictionary@hotmail.com", "lifeisawesome123", "Lauren", "Madison")
    with pytest.raises(ValueError) as excinfo:
        user_profile_sethandle(user_info["token"], "Happy Birthday Everyone")
    assert "Invalid handle" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        user_profile_sethandle(user_info["token"], "ireallyliketostudyeveryday")
    assert "Invalid handle" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        user_profile_sethandle(user_info["token"], "don't understand!!,,%%&&12")
    assert "Invalid handle" in str(excinfo.value)

def test_user_profile_sethandle_existing_handle():
    """Tests to check if the handle str set is used by another user

    Create 2 users, if user 1 changes handle to user 2, then error occur
    Or, if user 2 changes chanle to user 1, then error occur
    If it is, raise ValueError
    """

    func_startup()
    user1_info = auth_register("mermaid@gmail.com", "12345qwe678", "Madison", "Pumpkin")
    profile_data_user1 = user_profile(user1_info["token"], user1_info["u_id"])
    user2_info = auth_register("abcdefg@hotmail.com", "popsicle123", "Grace", "Clock")
    profile_data_user2 = user_profile(user2_info["token"], user2_info["u_id"])
    with pytest.raises(ValueError) as excinfo:
        user_profile_sethandle(user1_info["token"], profile_data_user2["handle_str"])
    assert "Handle is being used by another user" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        user_profile_sethandle(user2_info["token"], profile_data_user1["handle_str"])
    assert "Handle is being used by another user" in str(excinfo.value)

def test_user_profile_sethandle_successful():
    """Tests to check that a certain display is valid.

    Checks to see if the handle_str in user_profile is valid.
    """

    func_startup()
    user_info = auth_register("catsanddogs@gmail.com", "fooddelicious724", "Alice", "Wonderland")
    # Check for different cases of strings
    user_profile_sethandle(user_info["token"], "beef and pork")
    user_profile_sethandle(user_info["token"], "pizzaislife")
    user_profile_sethandle(user_info["token"], "mouse!!!")

def test_user_profiles_uploadphoto_invalid_url():
    """ Test that checks if the image url passed in by the user is valid or not
    """
    reset_auth_data()
    data.initialise_data()
    user_info = auth_register("davidshin@gmail.com", "badpassword321", "David", "Shin")
    with pytest.raises(ValueError) as excinfo:
        user_profiles_uploadphoto(user_info["token"], "https://fakeurl.com/hfialeuiew89.png",
                                  100, 100, 100, 100)
    assert "The image url is invalid" in str(excinfo.value), "Error message does not match"

def test_user_profile_uploadphoto_invalid_dimensions():
    """ Test that checks if the dimensions of the image is within the size range
    """
    reset_auth_data()
    data.initialise_data()
    user_info = auth_register("davidshin@gmail.com", "badpassword321", "David", "Shin")
    with pytest.raises(ValueError) as excinfo:
        user_profiles_uploadphoto(user_info["token"], "https://i.imgur.com/PXUhm8f.jpg", 0, 0,
                                  1000, 1000)
    assert "Image crop bounds exceed image size" in str(excinfo.value)

def test_user_profile_uploadphoto_invalid_format():
    """ Test that checks whether the image uploaded is of JPEG or JPG format
    """
    reset_auth_data()
    data.initialise_data()
    user_info = auth_register("davidshin@gmail.com", "badpassword321", "David", "Shin")
    with pytest.raises(ValueError) as excinfo:
        user_profiles_uploadphoto(user_info["token"], "https://i.imgur.com/Ut85DPw.png", 0, 0,
                                  150, 150)
    assert "Image is not in JPEG format" in str(excinfo.value), "Error message does not match"

def test_profile_uploadphoto_successful():
    """ Test to see if we can upload an image
    """
    reset_auth_data()
    data.initialise_data()
    user_info = auth_register("davidshin@gmail.com", "badpassword321", "David", "Shin")
    user_profiles_uploadphoto(user_info["token"], "https://i.imgur.com/PXUhm8f.jpg", 0, 0,
                              150, 150)

def test_profile_uploadphoto_successful_replace():
    """ Test to see if we can upload an image
    """
    reset_auth_data()
    data.initialise_data()
    user_info = auth_register("davidshin@gmail.com", "badpassword321", "David", "Shin")
    user_profiles_uploadphoto(user_info["token"], "https://i.imgur.com/PXUhm8f.jpg", 0, 0,
                              150, 150)
    user_profiles_uploadphoto(user_info["token"], "https://i.imgur.com/PXUhm8f.jpg", 0, 0,
                              200, 200)
