"""Unit tests for the admin_userpermission_change() function.

Designed to be run using the pytest utility.

The first user to be registered is an admin, who have the authority to change
the permission level of users.

ASSUMPTION These tests assume that the state of the program is reset after each test.
"""

import pytest

from server import auth
from server import admin
from server import data
from server.Error import AccessError, ValueError


def test_admin_userpermission_change_invalid_u_id():
    """Attempts to change the user permission of an Invalid user id.

    Should be thrown ValueError("Invalid user id")
    """

    auth.reset_auth_data()
    data.initialise_data()
    owner_info = auth.auth_register("adminemail@email.com", "chickensoup897", "Mills", "Wood")
    user_info = auth.auth_register("testemail@hotmail.com", "testpassword098", "Mr", "Test")
    with pytest.raises(ValueError) as excinfo:
        admin.admin_userpermission_change(owner_info["token"], user_info["u_id"] + 1, 2)
    assert "Invalid user id" in str(excinfo.value)

def test_admin_userpermission_change_invalid_permission_value():
    """Attempts to change the user permission for a valid u_id, but invalid permission ID.

    Should be thrown ValueError("Invalid permission ID")
    """

    auth.reset_auth_data()
    data.initialise_data()
    owner_info = auth.auth_register("adminemail@email.com", "chickensoup897", "Mills", "Wood")
    user_info = auth.auth_register("testemail@hotmail.com", "testpassword098", "Mr", "Test")
    with pytest.raises(ValueError) as excinfo:
        admin.admin_userpermission_change(owner_info["token"], user_info["u_id"], 4)
    assert "Invalid permission ID" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        admin.admin_userpermission_change(owner_info["token"], user_info["u_id"], 0)
    assert "Invalid permission ID" in str(excinfo.value)

def test_admin_userpermission_change_unauthorised_attempt():
    """Attempts to change the user permission of another user while having
       insufficient privileges.

    Should be thrown AccessError("User permission change attempted with insufficient privileges")
    """

    auth.reset_auth_data()
    data.initialise_data()
    owner_info = auth.auth_register("adminemail@email.com", "chickensoup897", "Mills", "Wood")
    user1_info = auth.auth_register("user1@hotmail.com", "testpassword094", "Mrs", "Test")
    user2_info = auth.auth_register("user2@hotmail.com", "password098", "Mr", "Test")
    with pytest.raises(AccessError) as excinfo:
        admin.admin_userpermission_change(user1_info["token"], user2_info["u_id"], 2)
    assert "User permission change attempted with insufficient privileges" in str(excinfo.value)

    admin.admin_userpermission_change(owner_info["token"], user1_info["u_id"], 2)
    with pytest.raises(AccessError) as excinfo:
        admin.admin_userpermission_change(user1_info["token"], user2_info["u_id"], 1)
    assert "User permission change attempted with insufficient privileges" in str(excinfo.value)

def test_admin_userpermission_change_successful():
    """Tests successful scenario for changing a user permission.

    An admin changes the user permission of a user to admin level.
    This change is tested by ensuring that this newly promoted admin is
    able to change the user permission of another user.
    Tests that both owners and admins can promote to admin.
    ASSUMPTION therefore, this test assumes that the feature of the
               admin_userpermission_change() function to throw an error when a user with
               insufficient privileges attempts to call the function is fully functional.
               This feature is covered by the previous test. i.e. the previous test
               must pass in order for this test to be valid.
    """

    auth.reset_auth_data()
    data.initialise_data()
    owner_info = auth.auth_register("adminemail@email.com", "chickensoup897", "Mills", "Wood")
    user1_info = auth.auth_register("user1@hotmail.com", "testpassword094", "Mrs", "Test")
    user2_info = auth.auth_register("user2@hotmail.com", "password098", "Mr", "Test")
    admin.admin_userpermission_change(owner_info["token"], user1_info["u_id"], 2)
    admin.admin_userpermission_change(user1_info["token"], user2_info["u_id"], 2)
