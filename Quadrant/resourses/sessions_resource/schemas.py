from marshmallow import Schema, fields

from Quadrant.resourses.common_schemas import SuccessResponseSchema


class UserSessionSchema(Schema):
    session_id = fields.Int()
    ip_address = fields.IP()
    started_at = fields.DateTime()
    is_alive = fields.Bool()


class UserSessionsPageSchema(Schema):
    sessions = fields.List(UserSessionSchema)


class SessionTerminationResponseSchema(SuccessResponseSchema):
    message = fields.Str()
    terminated_session_id = fields.Int()