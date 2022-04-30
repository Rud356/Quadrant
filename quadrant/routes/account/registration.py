from fastapi.responses import RedirectResponse

from pydantic import BaseModel
from ..router import api_router


class RegistrationBody(BaseModel):
    nickname: str
    login: str
    password: str


@api_router.route(
    "/account/register",
    methods=["POST"]
)
async def register_account(
    registration_details: RegistrationBody
) -> RedirectResponse:
    pass
