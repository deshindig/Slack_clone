""" Contains all the features available to Slackr admins. """

from server import auth
from server import data
from server.Error import AccessError

def admin_userpermission_change(token, u_id, permission_id):
    """ Changes the user permission of an owner, given that the promoter has
        sufficient privileges.

        An owner can promote or demote anyone.
        An admin can promote to or demote admins, but cannot promote to or
        demote owners.
        A user can not promote nor demote anyone.
    """

    auth_u_id = auth.verify_token(token)
    server_data = data.load_data()
    subject_user = server_data.return_user(u_id)
    auth_user = server_data.return_user(auth_u_id)

    if (auth_user.get_permission_id() == data.User.USER_ID or
            (auth_user.get_permission_id() == data.User.ADMIN_ID and
             permission_id == data.User.OWNER_ID) or
             subject_user.get_permission_id == data.User.OWNER_ID):
        raise AccessError("User permission change attempted with insufficient privileges")

    subject_user.set_permission_id(permission_id)
    data.save_data(server_data)
