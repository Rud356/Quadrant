### Route: /api/endpoints/<endpoint_id>/messages
Methods: GET  
Description:  
Requires: endpoint id  
Response: 100 messages from last one including it  


### Route: /api/endpoints/<endpoint_id>/messages/<message_id>
Methods: GET  
Description:  
Requires: endpoint id, message id  
Response: 200 (message object), 403, 404  


### Route: /api/endpoints/<endpoint_id>/messages/<message_id>/from
Methods: GET  
Description:  
Requires: endpoint id, message id  
Response: 100 messages from setted one without it  


### Route: /api/endpoints/<endpoint_id>/messages/<message_id>/after
Methods: GET  
Description:  
Requires: endpoint id, message id  
Response: 100 messages after setted one without it  


### Route: /api/endpoints/<endpoint_id>/messages/pinned
Methods: GET  
Description:  
Requires: endpoint id  
Response: 100 pinned newest messages with newest one  


### Route: /api/endpoints/<endpoint_id>/messages/pinned/<message_id>/pinned/from
Methods: GET  
Description:  
Requires: endpoint id, message id  
Response: 100 pinned messages from setted one excluding it  


### Route: /api/endpoints/<endpoint_id>/messages
Methods: POST  
Description:  
Yet to add  


### Route: /api/endpoints/<endpoint_id>/messages/<message_id>
Methods: GET  
Description:  
Requires: endpoint id, message id  
Response: 200 (message object), 403, 404  


### Route: /api/endpoints/<endpoint_id>/messages/<message_id>
Methods: DELETE  
Description:  
Requires: endpoint id, message id and  
optionally can have `force` url param (default is false)  
Response: 200, 204, 403, 404  


### Route: /api/endpoints/<endpoint_id>/messages/<message_id>
Methods: PATCH  
Description:  
Yet to add  


### Route: /api/endpoints/<endpoint_id>/messages/<message_id>/pin
Methods: PATCH  
Description:  
Requires: endpoint id, message id  
Response: 200, 204 (if no such message), 403, 404  


### Route: /api/endpoints/<endpoint_id>/messages/<message_id>/unpin
Methods: PATCH  
Description:  
Requires: endpoint id, message id  
Response: 200, 204 (if no such message), 403, 404  


