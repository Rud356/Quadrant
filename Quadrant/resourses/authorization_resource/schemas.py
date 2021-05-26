from marshmallow import fields

from Quadrant.resourses.user_resource.schemas import UserPrivateSchema


class UserLoginResponseSchema(UserPrivateSchema):
    authorized = fields.Boolean(default=True)
    current_session_id = fields.Integer()
