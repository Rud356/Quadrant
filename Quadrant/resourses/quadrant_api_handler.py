from typing import Any, Dict, Optional, Union

from rapidjson import JSONDecodeError
from sqlalchemy.ext.asyncio import AsyncSession
from tornado.web import RequestHandler

from Quadrant.models.db_init import Session
from Quadrant.models.users_package import OauthUserAuthorization, User, UserInternalAuthorization, UserSession
from Quadrant.resourses.middlewares import authorization_middleware
from Quadrant.resourses.utils import JsonWrapper


class QuadrantAPIHandler(RequestHandler):
    session: AsyncSession
    user: Optional[User]
    auth_user: Optional[Union[OauthUserAuthorization, UserInternalAuthorization]]
    user_session: Optional[UserSession]
    json_data: Optional[Dict[str, Any]]

    def get_current_user(self) -> Optional[Union[UserInternalAuthorization, OauthUserAuthorization]]:
        return getattr(self, 'auth_user', None)

    async def prepare(self):
        self.set_header("Content-Type", 'application/json')

        self.session = Session()
        self.auth_user, self.user_session = await authorization_middleware(self, self.session)
        self.user = getattr(self.auth_user, 'user', None)
        self.json_data = None

        if self.request.headers.get("Content-Type") == "application/json":
            try:
                self.json_data = JsonWrapper.loads(self.request.body)

            except JSONDecodeError:
                pass

    async def on_finish(self) -> None:
        await self.session.close()
