
# Seprinciples

-   Overhaul the method of storing data from a large collection of various dictionaries containing the objects (User, Channel, Message) into a ServerData class. This use of a centralised ServerData allows us to deal with the data and functionality related to the data reduces various design ?smells?. The current code is now more mobile and less opaque along with it being decoupled. Originally, when the data was dealt with directly, the base code is (auth, admin, etc.) was filled with repetitive and redundant data that interacts with the data layer. The ServerData class new interfaces decouple the data layer from the system's back-end. If the storage method were to be altered or changed, the behaviour of the ServerData class can quickly and easily be changed. This reduces the viscosity and rigidity of the system.
    
-   The new application layer of the systems back-end code is now more mobile, and less opaque for developers in the future. The original nested dictionary accessing method has now been completely removed and replaced with simple calls to the ServerData class.
    
-   New additions to the list of helper functions, is_registered_email, is_registered_handle, get_u_id_from_email, and generate_unique_handle that parse through all user objects are made methods of the ServerData class. This added level of abstraction also improves the simplicity of our code as all of our server data no longer need to pass through the helper functions.
    
-   Overall, a lot of "helper" functionality such as incrementing ID counter and returning a new ID is abstracted away to methods in the ServerData class. The abstraction to a method acts upon the DRYKISS principle.
    
-   Many repeated "raise Exception" statements were moved into the data classes themselves. For example, if an invalid u_id, channel_id, or message_id is being accessed, the ServerData class checks for this in the respective "return" method. This reduces the "needless repetition", and makes the code more mobile, as the data classes can be accessed more independently if these checks are made.
    
-   Needlessly long method names such as "get_message_u_id" were simplified using OOP standard practice. The behaviour of a method class depends on the object it is called upon, which the user of the object has access to. Thus there is no need to specify the class name in the method. This reduces the system?s obscurity, making it easier to read and maintain in the future.
    
-   In standup, our previous approach was to create a message object every time standup_send was called. Now, we simply store the name of the caller and message body. This significantly reduces needless complexity.
    
-   Within the user function test, a new function was added called data initialise to help set up the environment for every test. This includes the functions used to reset the server data and create the accounts/channels used in the test. This improvement utilises the DRKISS principle.
    
-   Within the standup function test, the function was added to set up the environment for all the preceding tests. The publicity of the channel is determined simply via a boolean check.

