### Route: /api/friends
Methods: GET
Description:
Response: list of public users that are friends

### Route: /api/blocked
Methods: GET
Description:
Response: list of public users

### Route: /api/outgoing_requests
Methods: GET
Description:
Response: list of public users that are sent pendings from you

### Route: /api/outgoing_requests/<id>
Methods: DELETE
Description:
Requests: id of user we sent request to cancel  
Response: 200, 400, 403, 404

### Route: /api/incoming_requests
Methods: GET
Description:
Response: list of public users that are sent pendings to you

### Route: /api/incoming_requests/<id>
Methods: POST
Description:
Requests: id of friend request sender we're responding to  
Optionally may set url param `accept` to True to accept (default: decline)  
Response: 200, 400, 404

### Route: /api/friends/<id>
Methods: POST
Description:
Requests: id of reciever of friend request  
Response: 200, 403, 404

### Route: /api/friends/request
Methods: POST
Description:
Requests: code as url param of reciever of friend request  
Response: 200, 400, 404

### Route: /api/friends/<id>
Methods: DELETE
Description:
Requests: id of reciever of friend request  
Response: 200, 400, 404

### Route: /api/blocked/<id>
Methods: POST
Description:
Request: blocking user id in url  
Response: 200, 204 (already blocked), 400

### Route: /api/blocked/<id>
Methods: DELETE
Description:
Request: unblocking user id in url  
Response: 200, 204 (already blocked), 400

