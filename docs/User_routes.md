### Route: /api/user/login
Methods: POST  
Description:  
Yet to add  


### Route: /api/user/logout
Methods: POST GET DELETE  
Description:  
Requires authorization!  
Response: "All is fine!" 200  


### Route: /api/user/register
Methods: POST  
Description:  
Yet to add  


### Route: /api/user/<id>
Methods: GET  
Description:  
Requires: user id in route  
Response: 400 or public user  


### Route: /api/user/me
Methods: GET  
Description:  
Response: private user  


### Route: /api/user/me
Methods: DELETE  
Description:  
Yet to add  


### Route: /api/user/keep-alive
Methods: GET  
Description:  
Response: ok  


### Route: /api/user/update_token
Methods: POST  
Description:  
Yet to add  


### Route: /api/me/nick
Methods: POST  
Description:  
Requires: new_nick as url parameter  
Validations:  
`0 < nick length <= 25`  
Responses: 200, 400  


### Route: /api/me/friend_code
Methods: POST  
Description:  
Requires: code as url parameter  
Validations:  
`0 < code length <= 50`  
Responses: 200, 400  


### Route: /api/me/status/<int:new_status>
Methods: POST  
Description:  
Requires: status code in url  
Validations:  
`0 <= status <= 4`  
Responses: 200, 400  


### Route: /api/me/text_status
Methods: POST  
Description:  
Yet to add  


