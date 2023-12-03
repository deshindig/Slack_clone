# Plan:

When approaching implementing the functions in iteration 2, the team has decided upon a data manipulation based plan. The iteration would be split into multiple parts based on how they manipulate data and will be organized as so. All functions which input data into the server will be implemented first, followed by testing to ensure all data is correctly and completely inserted. This flow is to prevent roadblocks based on dependency on other functions where functions may require previously created functions to be completed before using it.

As well as being a manipulation based plan, each member shall be in charge of a singular aspect of the slack application. These aspects consist of channels, users, messages, etc. This means that since each member specialises to one set of functions, members would not need to learn and or relearn various functions from different aspects of the code, thus streamlining the process making it faster. While it may be that certain other aspects may require learning and assistance from other members, it will still minimize the broadness of knowledge which each member needs to learn and speed up the workflow.

The steps of implementation will go as follows: 
 * Firstly, Implement all functions regarding data insertion to the server and test accordingly. Example functions such as message_send, channel_create, etc. These can easily be done and easily checked and tested.
 * Secondly, implement all functions regarding data deletion. Since data insertion now works, we can test deletion with the help of working insertion functions and catch any errors early on. 
 * Thirdly, we will implement all functions related to data manipulations. Example functions such as message_edit, channel_removeowner, etc. This means that given we have completed deletion, the team should now have a good idea of how to access each specific component of an aspect and manipulate them. Up to this point, we have assumed that the user has all the correct authority to manipulate data. 
 * During stage 1 through 3, we will have a member focusing on the authentication of data and will work with other members as each stage is completed.
 * Finally, implement all remaining functions. Given that all based manipulation, deletion, and insertion of data has been correctly implemented and understood, all remaining functions are a combination of aspects so we should have a good understanding of how to implement the functions.

