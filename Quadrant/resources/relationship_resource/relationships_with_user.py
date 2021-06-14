from uuid import UUID

from fastapi import Depends, Request, status

from .router import router
from Quadrant.resources.utils import require_authorization
from Quadrant.models import users_package
from Quadrant.schemas import HTTPError, relations_schema


@router.get(
    "/api/v1/relations/exact/{with_user_id}",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.RelationWithUser},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPError},
    },
    tags=["Users relationships"]
)
async def check_relationship_status(with_user_id: UUID, request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    relation = await users_package.UsersRelations.get_exact_relationship_status(
        db_user.id, with_user_id, session=sql_session
    )
    return {"with_user_id": with_user_id, "status": relation}
