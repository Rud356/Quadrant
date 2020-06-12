### Route: /api/user/set_image
Methods: POST
Description:
Payload: file ["image"]  
Limits: 4MB file of gif, jpeg, png, webp formats  
Response codes: 200, 400, 401

### Route: /api/user/<user_id>/profile_pic
Methods: GET
Description:
Requires: user_id in route  
Response: 404, file

### Route: /api/files/upload
Methods: POST
Description:
Requires: files  
Response: list of files names

### Route: /api/files/<file_name>
Methods: GET
Description:
Requires: file name in route  
Response: 404, file

