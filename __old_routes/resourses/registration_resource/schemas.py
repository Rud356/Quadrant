from marshmallow import Schema, fields


class UserRegistrationSchema(Schema):
    username = fields.String(required=True, validate=[fields.validate.Length(min=1, max=50)])
    # regex taken from: https://stackoverflow.com/questions/19605150/
    login = fields.String(
        required=True, validate=[
            fields.validate.Length(min=8, max=128),
            fields.validate.Regexp(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")
        ]
    )
    password = fields.String(
        required=True, validate=[
            fields.validate.Length(min=8, max=128),
            fields.validate.Regexp(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,128}$")
        ]
    )