
# Teamwork:

  

Unlike iteration 1 and 2, iteration 3 did not require as much attention as we thought we needed. We initially believed before iteration 3 that we may need to further expand on the functionality of the slackr web app, so in preparation for this, we completed our implementation between the frontend and the backend. The advantage we gained from this was that we had a strong understanding of our system so when it came to implementing the remaining added functionality took no time.

  

Furthermore, because of this, the team did not require to meet with each other for standups as much as we did previously and reduced it to a per weekly basis. This added time allowed us to carefully analyse the implementation and figure out methods to refactor and simplify the program for efficiency reasons. For the times where the team did meet up, we generally discussed on various aspects of the code we believed we could simplify without completely changing the method to which we interfaced with the functions. Because of our previous anticipation and preparation for added functionality, functions in the system had complicated data structures which added unnecessary complexities and made it opaque. Some ideas of reducing repetition in the program were considered but ultimately decided against it due to it adding additional dependencies and further reducing understanding of the code.

  

By this iteration, all team members are all comfortable with their function category within the system, so when it came to refactoring we focused heavily on our own. However because of the heavy dependencies on how data was being stored and accessed, we decided on having the data refactoring take place on a separate branch, this is to allow for the refactoring of our test to continue with the current system as other members worked on refactoring the functionality. The major refactoring challenge which we faced was to refactor the method in which the data was stored. The original system kept large dictionaries of objects of other classes from other functions. This reduced redundant data within our systems and improved overall understanding of the system, especially between the team members.

  

Finally, additions made to functionality tests was to ensure firstly that all tests required by the specification are covered and secondly, that any additional test which the team believed to be necessary for other functions are to be added. Full coverage was also the team focus during refactorisation to ensure our final system is stable. Pylint was also used to have the system comply with industry standards of styling. Final stress testing on the system was also performed through pytesting and the frontend directly to have the assurance that the system is fully operational.

