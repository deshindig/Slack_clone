""" Unit tests for the functions with the auth.auth_ prefix.

Designed to be run using the pytest utility.

For each function, test every possible unsuccessful scenario, i.e. scenarios
where errors are raised.

Also test successful scenarios and ensure that the function did what it was
supposed to do.

ASSUMPTION These tests assume that the state of the program is reset after each test.
"""

import pytest

from server import data
from server import auth
from server import user
from server.Error import AccessError, ValueError


def test_auth_login_invalid_email():
    """Attempts multiple logins with variously invalid email addresses.

    Examples of invalid emails: davidshin@gmail, davidshin.com, davidshin.
    Should be thrown ValueError("Login attempted with invalid email")
    """

    auth.reset_auth_data()
    data.initialise_data()
    with pytest.raises(ValueError) as excinfo:
        auth.auth_login("mrbean@gmail", "safepassword123")
    assert "Login attempted with invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        auth.auth_login("mrbean.com", "safepassword123")
    assert "Login attempted with invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        auth.auth_login("@gmail.com", "safepassword123")
    assert "Login attempted with invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        auth.auth_login("mrbean", "safepassword123")
    assert "Login attempted with invalid email" in str(excinfo.value)


def test_auth_login_unregistered_email():
    """Attempts a login with an unregistered email address.

    Should be thrown ValueError("Unregistered email")
    """

    auth.reset_auth_data()
    data.initialise_data()
    with pytest.raises(ValueError) as excinfo:
        auth.auth_login("mrbean@gmail.com", "ilovemrbean123")
    assert "Unregistered email" in str(excinfo.value)

def test_auth_login_incorrect_password():
    """Attempts a login with a registered email, but with incorrect password.

    Should be thrown ValueError("Login attempted with incorrect password")
    """

    auth.reset_auth_data()
    data.initialise_data()
    register_user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    auth.auth_logout(register_user_info["token"])
    with pytest.raises(ValueError) as excinfo:
        auth.auth_login("mrbean@gmail.com", "ihatemrbean321")
    assert "Login attempted with incorrect password" in str(excinfo.value)

def test_auth_login_successful():
    """Tests a successful login scenario.

    Registers the user, then logs the user out.
    Logs the user back in with the credentials used for registration.
    Asserts that the u_id from registration matches u_id from logging in.
    Asserts that the session token returned is valid.
    """

    auth.reset_auth_data()
    data.initialise_data()
    register_user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    auth.auth_logout(register_user_info["token"])
    login_user_info = auth.auth_login("mrbean@gmail.com", "ilovemrbean123")
    assert login_user_info["u_id"] == register_user_info["u_id"]
    auth.verify_token(login_user_info["token"])

def test_auth_logout_unmatching_token():
    """Attempts logout with an invalid session token.

    Asserts that the session token for the current session remains valid.
    """

    auth.reset_auth_data()
    data.initialise_data()
    register_user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    logout_info = auth.auth_logout(register_user_info["token"] + "273818")
    assert not logout_info["is_success"]
    auth.verify_token(register_user_info["token"])

def test_auth_logout_successful():
    """Attempts a successful logout scenario.

    Asserts that the session token is invalidated after logging out.
    """

    auth.reset_auth_data()
    data.initialise_data()
    register_user_info = auth.auth_register("mrbean@gmail.com", "ilovemrbean123", "Mr", "Bean")
    logout_info = auth.auth_logout(register_user_info["token"])
    assert logout_info["is_success"]
    with pytest.raises(AccessError) as excinfo:
        auth.verify_token(register_user_info["token"])
    assert "Invalid token" in str(excinfo.value)

def test_auth_register_invalid_email():
    """Attempts multiple registrations with variously invalid email addresses.

    Examples of invalid emails: davidshin@gmail, davidshin.com, davidshin.
    Should be thrown ValueError("Invalid email")
    """

    auth.reset_auth_data()
    data.initialise_data()
    with pytest.raises(ValueError) as excinfo:
        auth.auth_register("mrbean@gmail", "safepassword123", "Mr", "Bean")
    assert "Invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        auth.auth_register("mrbean.com", "safepassword123", "Mr", "Bean")
    assert "Invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        auth.auth_register("@gmail.com", "safepassword123", "Mr", "Bean")
    assert "Invalid email" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        auth.auth_register("mrbean", "safepassword123", "Mr", "Bean")
    assert "Invalid email" in str(excinfo.value)

def test_auth_register_unavailable_email():
    """Attempts registration with an email address already in use by another user.

    ASSUMPTION Assumes that successful registration works as intended,
               i.e. the first user registered is successfully registered.
    Should be thrown ValueError("Registration attempted with unavailable email")
    """

    auth.reset_auth_data()
    data.initialise_data()
    auth.auth_register("mrbean@gmail.com", "safepassword123", "Mr", "Bean")
    with pytest.raises(ValueError) as excinfo:
        auth.auth_register("mrbean@gmail.com", "qwertyuiop101", "Totallynot", "MrBean")
    assert "Registration attempted with unavailable email" in str(excinfo.value)

def test_auth_register_invalid_password():
    """Attempts registration with invalid password, i.e. < 5 characters.

    Should be thrown ValueError("Invalid password")
    """

    auth.reset_auth_data()
    data.initialise_data()
    with pytest.raises(ValueError) as excinfo:
        auth.auth_register("mrbean@gmail.com", "car", "Mr", "Bean")
    assert "Invalid password" in str(excinfo.value)

def test_auth_register_invalid_first_name():
    """Tests registration attempt with invalid first name, i.e. > 50 characters.

    Should be thrown ValueError("Invalid first name")
    """

    auth.reset_auth_data()
    data.initialise_data()
    with pytest.raises(ValueError) as excinfo:
        auth.auth_register("mrbean@gmail.com", "validpassword123", "M"*51, "Bean")
    assert "Invalid first name" in str(excinfo.value)

def test_auth_register_invalid_last_name():
    """Tests registration attempt with invalid last name, i.e. > 50 characters.

    Should be thrown ValueError("Invalid last name")
    """

    auth.reset_auth_data()
    data.initialise_data()
    with pytest.raises(ValueError) as excinfo:
        auth.auth_register("mrbean@gmail.com", "validpassword123", "Mr", "B"*51)
    assert "Invalid last name" in str(excinfo.value)

def test_auth_register_successful():
    """Tests successful registration scenario.

    Checks that the returned token is valid.
    Ensures that user is actually registered by logging out then logging in
    using the registered credentials.
    ASSUMPTION Therefore, assumes that auth.auth_login() function works as intended.
    """

    auth.reset_auth_data()
    data.initialise_data()
    email, password = "mrbean@gmail.com", "validpassword123"
    user_info = auth.auth_register(email, password, "Mr", "Bean")
    auth.verify_token(user_info["token"])
    auth.auth_logout(user_info["token"])
    auth.auth_login(email, password)

def test_auth_register_handle_test():
    """Tests registration with different handle strings
    Checks to see if the handle strings are unique, i.e. not used by another user
    """
    auth.reset_auth_data()
    data.initialise_data()
    user1_info = auth.auth_register("mrbean@gmail.com", "validpassword123", "Daviddddddddd",
                                    "Shinnnnnnnnn")
    user2_info = auth.auth_register("drshin@gmail.com", "greatpwd212", "Daviddddddddd",
                                    "Shinnnnnnnnn")
    user3_info = auth.auth_register("drhao@gmail.com", "greatpwd2fsd12", "Daviddddddddd",
                                    "Shinnnnnnnnn")
    user1_profile = user.user_profile(user1_info["token"], user1_info["u_id"])
    user2_profile = user.user_profile(user2_info["token"], user2_info["u_id"])
    user3_profile = user.user_profile(user3_info["token"], user3_info["u_id"])
    assert user1_profile["handle_str"] != user2_profile["handle_str"]
    assert user1_profile["handle_str"] != user3_profile["handle_str"]
    assert user2_profile["handle_str"] != user3_profile["handle_str"]

def test_auth_passwordreset_reset_invalid_code():
    """Attempts password reset with an invalid code.

    Should be thrown ValueError("Invalid reset code")
    """

    auth.reset_auth_data()
    data.initialise_data()
    with pytest.raises(ValueError) as excinfo:
        auth.auth_passwordreset_reset("12312", "testpassword123")
    assert "Invalid reset code" in str(excinfo.value)

def test_auth_passwordreset_reset_invalid_password():
    """Attempts password reset with a valid code, but invalid password.

    An invalid password is less than 5 characters.
    get_reset_code() is a function that does the same thing as
    auth.auth_passwordreset_request(), but returns a reset code instead of emailing it.
    Should be thrown ValueError("Reset attempted with invalid password")
    """

    auth.reset_auth_data()
    data.initialise_data()
    email = "mrbean@gmail.com"
    auth.auth_register(email, "testpass1232", "Mr", "Bean")
    with pytest.raises(ValueError) as excinfo:
        auth.auth_passwordreset_reset(auth.auth_passwordreset_request(email), "hi!")
    assert "Invalid password" in str(excinfo.value)

def test_auth_passwordreset_reset_successful():
    """Tests a successful password reset scenario.

    get_reset_code() is a function that does the same thing as
    auth.auth_passwordreset_request(), but returns a reset code instead of emailing it.
    Ensures that the password has been truly changed by logging out, then
    logging back in using the new password.
    """

    auth.reset_auth_data()
    data.initialise_data()
    email = "mrbean@gmail.com"
    user_info = auth.auth_register(email, "unsafepassword123", "Mr", "Bean")
    new_password = "saferpassword9876"
    auth.auth_passwordreset_reset(auth.auth_passwordreset_request(email), new_password)
    auth.auth_logout(user_info["token"])
    auth.auth_login(email, new_password)
