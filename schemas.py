from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

from models import ActionType


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource_type: str


class ResourceCreate(ResourceBase):
    pass


class ResourceResponse(ResourceBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    name: str
    action: ActionType
    resource_id: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: str
    created_at: datetime
    resource: ResourceResponse

    class Config:
        from_attributes = True


class UserRoleBase(BaseModel):
    user_id: str
    role_id: str


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleResponse(UserRoleBase):
    id: str
    assigned_at: datetime
    role: RoleResponse

    class Config:
        from_attributes = True


class UserPermissionBase(BaseModel):
    user_id: str
    permission_id: str
    is_granted: bool = True


class UserPermissionCreate(UserPermissionBase):
    pass


class UserPermissionResponse(UserPermissionBase):
    id: str
    assigned_at: datetime
    permission: PermissionResponse

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str
    password_confirm: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None