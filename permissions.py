from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import UserRole, RolePermission, UserPermission, ActionType, Permission, Resource


def check_user_permission(
    db: Session,
    user_id: str,
    action: ActionType,
    resource_name: str
) -> bool:
    """Проверка разрешения пользователя на действие с ресурсом"""

    # Проверяем прямые разрешения пользователя
    user_permission = db.query(UserPermission).join(
        Permission, UserPermission.permission_id == Permission.id
    ).join(
        Resource, Permission.resource_id == Resource.id
    ).filter(
        UserPermission.user_id == user_id,
        Permission.action == action,
        Resource.name == resource_name
    ).first()

    if user_permission:
        return user_permission.is_granted

    # Проверяем разрешения через роли
    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()

    for user_role in user_roles:
        role_permission = db.query(RolePermission).join(
            Permission, RolePermission.permission_id == Permission.id
        ).join(
            Resource, Permission.resource_id == Resource.id
        ).filter(
            RolePermission.role_id == user_role.role_id,
            Permission.action == action,
            Resource.name == resource_name
        ).first()

        if role_permission:
            return True

    return False


def require_permission(action: ActionType, resource_name: str):
    """Декоратор для проверки разрешений"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Получаем db и user из аргументов
            db = None
            user = None

            for arg in args:
                if hasattr(arg, 'query'):  # Это сессия БД
                    db = arg
                elif hasattr(arg, 'id'):  # Это пользователь
                    user = arg

            if not db or not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Не удалось получить данные для проверки разрешений"
                )

            if not check_user_permission(db, str(user.id), action, resource_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Доступ запрещен"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator