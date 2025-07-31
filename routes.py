from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import *
from schemas import *
from utils import get_password_hash, verify_password, create_access_token
from dependencies import get_current_active_user
from datetime import datetime, timedelta
from permissions import *

router = APIRouter()


@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация пользователя"""
    # Проверка совпадения паролей
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароли не совпадают"
        )

    # Проверка существования пользователя
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    # Создание пользователя
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "Пользователь успешно зарегистрирован", "user_id": str(db_user.id)}


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Вход пользователя"""
    # Поиск пользователя
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    # Проверка активности
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Аккаунт деактивирован"
        )

    # Проверка пароля
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    # Создание токена
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Создание сессии
    session = UserSession(
        user_id=user.id,
        token=access_token,
        expires_at=datetime.utcnow() + access_token_expires
    )

    db.add(session)
    db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=session.expires_at,
        user=UserResponse.from_orm(user)
    )


@router.post("/logout")
async def logout(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Выход пользователя"""
    # Деактивация всех сессий пользователя
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).update({"is_active": False})
    db.commit()
    
    return {"message": "Успешный выход из системы"}


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """Получение профиля пользователя"""
    return UserResponse.from_orm(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
        user_data: UserUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Обновление профиля пользователя"""
    if user_data.name:
        current_user.name = user_data.name
    if user_data.email:
        current_user.email = user_data.email
    
    db.commit()
    db.refresh(current_user)
    return UserResponse.from_orm(current_user)


@router.delete("/profile")
async def delete_profile(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Удаление профиля пользователя"""
    # Деактивация пользователя
    current_user.is_active = False
    # Деактивация всех сессий
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    ).update({"is_active": False})
    db.commit()
    
    return {"message": "Профиль успешно удален"}


# Управление ролями
@router.post("/roles/", response_model=RoleResponse)
async def create_role(
        role_data: RoleCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Создание новой роли"""
    if not check_user_permission(db, str(current_user.id), ActionType.CREATE, "roles"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    db_role = Role(**role_data.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return RoleResponse.from_orm(db_role)


@router.get("/roles/", response_model=List[RoleResponse])
async def get_roles(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение списка ролей"""
    if not check_user_permission(db, str(current_user.id), ActionType.LIST, "roles"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    roles = db.query(Role).all()
    return [RoleResponse.from_orm(role) for role in roles]


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
        role_id: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение роли по ID"""
    if not check_user_permission(db, str(current_user.id), ActionType.READ, "roles"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль не найдена"
        )
    return RoleResponse.from_orm(role)


# Управление ресурсами
@router.post("/resources/", response_model=ResourceResponse)
async def create_resource(
        resource_data: ResourceCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Создание нового ресурса"""
    if not check_user_permission(db, str(current_user.id), ActionType.CREATE, "resources"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    db_resource = Resource(**resource_data.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return ResourceResponse.from_orm(db_resource)


@router.get("/resources/", response_model=List[ResourceResponse])
async def get_resources(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение списка ресурсов"""
    if not check_user_permission(db, str(current_user.id), ActionType.LIST, "resources"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    resources = db.query(Resource).all()
    return [ResourceResponse.from_orm(resource) for resource in resources]


# Управление разрешениями
@router.post("/permissions/", response_model=PermissionResponse)
async def create_permission(
        permission_data: PermissionCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Создание нового разрешения"""
    if not check_user_permission(db, str(current_user.id), ActionType.CREATE, "permissions"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    db_permission = Permission(**permission_data.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return PermissionResponse.from_orm(db_permission)


@router.get("/permissions/", response_model=List[PermissionResponse])
async def get_permissions(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение списка разрешений"""
    if not check_user_permission(db, str(current_user.id), ActionType.LIST, "permissions"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    permissions = db.query(Permission).all()
    return [PermissionResponse.from_orm(permission) for permission in permissions]


# Управление ролями пользователей
@router.post("/user-roles/", response_model=UserRoleResponse)
async def assign_role_to_user(
        user_role_data: UserRoleCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Назначение роли пользователю"""
    if not check_user_permission(db, str(current_user.id), ActionType.CREATE, "user_roles"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    db_user_role = UserRole(**user_role_data.dict())
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return UserRoleResponse.from_orm(db_user_role)


@router.get("/user-roles/", response_model=List[UserRoleResponse])
async def get_user_roles(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение списка ролей пользователей"""
    if not check_user_permission(db, str(current_user.id), ActionType.LIST, "user_roles"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    user_roles = db.query(UserRole).all()
    return [UserRoleResponse.from_orm(user_role) for user_role in user_roles]


# Управление разрешениями пользователей
@router.post("/user-permissions/", response_model=UserPermissionResponse)
async def assign_permission_to_user(
        user_permission_data: UserPermissionCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Назначение разрешения пользователю"""
    if not check_user_permission(db, str(current_user.id), ActionType.CREATE, "user_permissions"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    db_user_permission = UserPermission(**user_permission_data.dict())
    db.add(db_user_permission)
    db.commit()
    db.refresh(db_user_permission)
    return UserPermissionResponse.from_orm(db_user_permission)


@router.get("/user-permissions/", response_model=List[UserPermissionResponse])
async def get_user_permissions(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение списка разрешений пользователей"""
    if not check_user_permission(db, str(current_user.id), ActionType.LIST, "user_permissions"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    user_permissions = db.query(UserPermission).all()
    return [UserPermissionResponse.from_orm(user_permission) for user_permission in user_permissions]


# Бизнес-логика (примеры защищенных ресурсов)
@router.get("/products/")
async def get_products(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение списка продуктов"""
    if not check_user_permission(db, str(current_user.id), ActionType.LIST, "products"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    # Имитация данных продуктов
    products = [
        {"id": 1, "name": "Продукт 1", "price": 100},
        {"id": 2, "name": "Продукт 2", "price": 200},
        {"id": 3, "name": "Продукт 3", "price": 300}
    ]
    return {"products": products, "user": current_user.email}


@router.get("/products/{product_id}")
async def get_product(
        product_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение продукта по ID"""
    if not check_user_permission(db, str(current_user.id), ActionType.READ, "products"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    # Имитация данных продукта
    product = {
        "id": product_id,
        "name": f"Продукт {product_id}",
        "price": product_id * 100,
        "description": f"Описание продукта {product_id}"
    }
    return {"product": product, "user": current_user.email}


@router.get("/orders/")
async def get_orders(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение списка заказов"""
    if not check_user_permission(db, str(current_user.id), ActionType.LIST, "orders"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    # Имитация данных заказов
    orders = [
        {"id": 1, "customer": "Клиент 1", "total": 500},
        {"id": 2, "customer": "Клиент 2", "total": 750},
        {"id": 3, "customer": "Клиент 3", "total": 1200}
    ]
    return {"orders": orders, "user": current_user.email}


@router.get("/orders/{order_id}")
async def get_order(
        order_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение заказа по ID"""
    if not check_user_permission(db, str(current_user.id), ActionType.READ, "orders"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    # Имитация данных заказа
    order = {
        "id": order_id,
        "customer": f"Клиент {order_id}",
        "total": order_id * 250,
        "items": [
            {"product": "Продукт 1", "quantity": 2, "price": 100},
            {"product": "Продукт 2", "quantity": 1, "price": 200}
        ]
    }
    return {"order": order, "user": current_user.email}


@router.get("/customers/")
async def get_customers(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение списка клиентов"""
    if not check_user_permission(db, str(current_user.id), ActionType.LIST, "customers"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    # Имитация данных клиентов
    customers = [
        {"id": 1, "name": "Иван Иванов", "email": "ivan@example.com"},
        {"id": 2, "name": "Петр Петров", "email": "petr@example.com"},
        {"id": 3, "name": "Анна Сидорова", "email": "anna@example.com"}
    ]
    return {"customers": customers, "user": current_user.email}


@router.get("/customers/{customer_id}")
async def get_customer(
        customer_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Получение клиента по ID"""
    if not check_user_permission(db, str(current_user.id), ActionType.READ, "customers"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    # Имитация данных клиента
    customer = {
        "id": customer_id,
        "name": f"Клиент {customer_id}",
        "email": f"customer{customer_id}@example.com",
        "phone": f"+7-999-{customer_id:03d}-00-00"
    }
    return {"customer": customer, "user": current_user.email}