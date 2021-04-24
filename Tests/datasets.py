from Quadrant.models import users_package, async_session


@async_session
async def create_user(
    username: str, login: str, password: str, session
) -> users_package.user_auth.UserInternalAuthorization:
    return await users_package.user_auth.UserInternalAuthorization.register_user_internally(
        username, login, password, session=session
    )
