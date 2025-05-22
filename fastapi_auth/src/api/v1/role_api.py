from typing import Annotated, List
from uuid import UUID

from opentelemetry import trace
from opentelemetry.trace import SpanKind
from src.core.user_core import current_superuser, current_user
from src.models.user import User
from src.schemas.response_schema import ResponseSchema
from src.schemas.role_schema import RoleCreate, RoleGetFull, RoleUpdate
from src.services.role_service import RoleService, get_role_service

from fastapi import APIRouter, Depends, Path, Request

router = APIRouter()
tracer = trace.get_tracer(__name__)


@router.get("/all", response_model=List[RoleGetFull], summary="Get all roles", description="Get all roles")
async def get_all_roles(
    request: Request, role_service: RoleService = Depends(get_role_service), user: User = Depends(current_user)
) -> List[RoleGetFull]:
    with tracer.start_as_current_span(
        "auth.roles.all", kind=SpanKind.SERVER, attributes={"http.request_id": request.headers.get("X-Request-Id")}
    ) as span:
        try:
            roles = await role_service.get_all()
            span.set_attribute("roles_count", len(roles))
            return roles
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


@router.post("/", response_model=RoleGetFull, summary="Create new role", description="Create new role")
async def create_role(
    request: Request,
    role_data: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    user: User = Depends(current_superuser),
) -> RoleGetFull:
    with tracer.start_as_current_span(
        "auth.roles.create_role",
        kind=SpanKind.SERVER,
        attributes={"http.request_id": request.headers.get("X-Request-Id")},
    ) as span:
        try:
            role = await role_service.create(role_data)
            span.set_attribute("role_create", True)
            return role
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


@router.patch(
    "/{role_id}", response_model=RoleGetFull, summary="Update existing role", description="Update existing role"
)
async def update_role(
    request: Request,
    role_id: Annotated[
        UUID,
        Path(
            title="role id",
            description="Role id for the item to search in the database",
        ),
    ],
    data: RoleUpdate,
    role_service: RoleService = Depends(get_role_service),
    user: User = Depends(current_superuser),
) -> RoleGetFull:
    with tracer.start_as_current_span(
        "auth.roles.update_role",
        kind=SpanKind.SERVER,
        attributes={"role_id": role_id, "http.request_id": request.headers.get("X-Request-Id")},
    ) as span:
        try:
            role = await role_service.update(role_id, data)
            span.set_attribute("role_update", True)
            return role
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


@router.delete(
    "/{role_id}", response_model=ResponseSchema, summary="Delete existing role", description="Delete existing role"
)
async def delete_role(
    request: Request,
    role_id: Annotated[
        UUID,
        Path(
            title="role id",
            description="Role id for the item to search in the database",
        ),
    ],
    role_service: RoleService = Depends(get_role_service),
    user: User = Depends(current_superuser),
) -> ResponseSchema:
    with tracer.start_as_current_span(
        "auth.roles.delete_role",
        kind=SpanKind.SERVER,
        attributes={"role_id": role_id, "http.request_id": request.headers.get("X-Request-Id")},
    ) as span:
        try:
            await role_service.delete(role_id)
            role_delete = ResponseSchema(detail="Role deleted successfully")
            span.set_attribute("role_delete", True)
            return role_delete
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise
