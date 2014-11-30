Connect-Server
==============

The server side support for the connect app

to authenticate a user: 
connect.sol-union.com/auth.py?code=...

where code stores the moves authentication code

to refresh an authentication
connect.sol-union.com/auth.py?refresh_token=...

where refresh_token stores the moves refresh token

to update user data and retreive suggestions
connect.sol-union.com/update.py?user=...

where user stores the moves user id

to update the current user location
conenct.sol-union.com/move.py?user=...&lat=...&lon=...

to upload a json with friend data
connect.sol-union.com/friends.py?user=...

put the json in post as 'json'

to access the model manually (temporary)
connect.sol-union.com/model.py?user=...

