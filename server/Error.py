""" Custom error classes used by Slackr. """

class AccessError(Exception):
    """ Error raised when user has invalid authentication/authorisation. """

    pass

class ValueError(Exception):
    """ Error raised when there is an invalid input from the front-end, or some
    other non-auth error arises.
    """

    pass
