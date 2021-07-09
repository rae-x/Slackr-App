# Assumptions

## F09A-while_true Project Iteration 1

1. Channel IDs and User IDs are generated sequentially as they are created, starting with 1
2. Parameter "start" in "channel\_messages" function must be greater than or equal to 0
3. Trying to invite the an existing user of a channel to the same channel will result in an AccessError
4. Tokens are alphanumeric strings with a length of 16
5. Passwords must be no more than 64 characters long
6. An AccessError is raised when channel\_join is called when the user is already in the channel
7. When a user creates a new channel, they join automatically and become an owner of it
8. Searching using a blank query (empty string) returns an empty list
9. Searching is case insensitive
10. Searching ignores trailing and leading whitespace
11. Passing an invalid token to search results in an AccessError
12. Passing an invalid token to users_all results in an AccessError
13. auth_register automatically logs a user in
14. Channel Ids are numbered in order of creation (first channel made has id 1, second has 2, etc)
15. Channel Ids are never an empty string
16. Any function that acts as a void (i.e. in the spec return type is {}), returns an empty dictionary ( {} )
17. Message IDs only contain numbers and are never an empty string
