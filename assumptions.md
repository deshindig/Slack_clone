# Assumptions:

 * The state of the program, e.g. user registration data, is reset after every test.
 * For message_test functions, I assume that no channel_id can ever go to a negative value
 * For message_test functions, I assume that there will only be 1 message of id 1 which will be used during testing
 * For message_test functions, I assume that the token are used for user verification and the correct tokens in any case will be ?12345? and all wrong token will be ?67890?
 * The return type of every function is a dictionary with every return variable stored in a key which is a string of the variable name.
 * For every single test that uses other back-end functions to set up the scenario for the test, assume all of the back-end functions work as expected.
 * For functions that require calling itself again to verify that the function performed as expected, assume that the other tests for that function pass, and therefore the other feature of that function is working as intended.
 * For example, therefore, the successful test for the admin_userpermission_change() function assumes that the feature of the function to throw an error when a user with insufficient privileges attempts to call the function is fully functional. This feature is covered by the previous test. i.e. the previous test must pass in order for this test to be valid.
 * In the start of every function, we assume that all the data is reset, that is a user is required to register for an account
 * When stand up is being called, we assume that the user starting the standup must send messages before they call the function
 * When you set up your first name and last name in the set user name function, it is required that it can not be more than 50 characters, but we also assume that you can use special characters in your name (e.g. !!! ,,,, :::)
 * When a user calls the function standup_send, we assume that a startup has previously been called and has started (that is, a standup must be successfully been called before standup_send take effect)
 * For the standup functions, we test for whether a user is inside a channel where the message is sent. We then assume that a public and private channel must be included in the test, as a standup could be started from either a public/private channel.
 * The search function works without any regard to the channel the messages are in, so the search function will search all the channels the user is in regardless of the specific details of the channels.
 * The user can see all the channels, public or private. However, they cannot join private channels without admin privilege.

 * Channel join and invite returns an error if the user is already in the channel.
 * A user can select a react_id even if it is already in a message. This will add them to the list of users who have chosen that reaction.
