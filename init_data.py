from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, Role, Resource, Permission, UserRole, RolePermission, UserPermission, ActionType
from utils import get_password_hash
import uuid


def init_test_data():
    """Инициализация тестовых данных"""
    # Сначала создаем все таблицы
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже данные в базе
        existing_roles = db.query(Role).count()
        if existing_roles > 0:
            print("Тестовые данные уже существуют в базе данных!")
            return
        
        # Создание ролей
        admin_role = Role(
            id=str(uuid.uuid4()),
            name="admin",
            description="Администратор системы"
        )
        
        manager_role = Role(
            id=str(uuid.uuid4()),
            name="manager", 
            description="Менеджер"
        )
        
        user_role = Role(
            id=str(uuid.uuid4()),
            name="user",
            description="Обычный пользователь"
        )
        
        db.add_all([admin_role, manager_role, user_role])
        db.commit()
        
        # Создание ресурсов
        users_resource = Resource(
            id=str(uuid.uuid4()),
            name="users",
            description="Пользователи системы",
            resource_type="user_management"
        )
        
        roles_resource = Resource(
            id=str(uuid.uuid4()),
            name="roles",
            description="Роли пользователей",
            resource_type="role_management"
        )
        
        permissions_resource = Resource(
            id=str(uuid.uuid4()),
            name="permissions",
            description="Разрешения",
            resource_type="permission_management"
        )
        
        products_resource = Resource(
            id=str(uuid.uuid4()),
            name="products",
            description="Продукты",
            resource_type="business"
        )
        
        orders_resource = Resource(
            id=str(uuid.uuid4()),
            name="orders",
            description="Заказы",
            resource_type="business"
        )
        
        customers_resource = Resource(
            id=str(uuid.uuid4()),
            name="customers",
            description="Клиенты",
            resource_type="business"
        )
        
        db.add_all([users_resource, roles_resource, permissions_resource, 
                   products_resource, orders_resource, customers_resource])
        db.commit()
        
        # Создание разрешений для пользователей
        user_permissions = []
        for action in ActionType:
            user_permissions.append(Permission(
                id=str(uuid.uuid4()),
                name=f"{action.value}_users",
                action=action,
                resource_id=users_resource.id,
                description=f"Разрешение на {action.value} пользователей"
            ))
        
        # Создание разрешений для ролей
        role_permissions = []
        for action in ActionType:
            role_permissions.append(Permission(
                id=str(uuid.uuid4()),
                name=f"{action.value}_roles",
                action=action,
                resource_id=roles_resource.id,
                description=f"Разрешение на {action.value} ролей"
            ))
        
        # Создание разрешений для разрешений
        perm_permissions = []
        for action in ActionType:
            perm_permissions.append(Permission(
                id=str(uuid.uuid4()),
                name=f"{action.value}_permissions",
                action=action,
                resource_id=permissions_resource.id,
                description=f"Разрешение на {action.value} разрешений"
            ))
        
        # Создание разрешений для продуктов
        product_permissions = []
        for action in ActionType:
            product_permissions.append(Permission(
                id=str(uuid.uuid4()),
                name=f"{action.value}_products",
                action=action,
                resource_id=products_resource.id,
                description=f"Разрешение на {action.value} продуктов"
            ))
        
        # Создание разрешений для заказов
        order_permissions = []
        for action in ActionType:
            order_permissions.append(Permission(
                id=str(uuid.uuid4()),
                name=f"{action.value}_orders",
                action=action,
                resource_id=orders_resource.id,
                description=f"Разрешение на {action.value} заказов"
            ))
        
        # Создание разрешений для клиентов
        customer_permissions = []
        for action in ActionType:
            customer_permissions.append(Permission(
                id=str(uuid.uuid4()),
                name=f"{action.value}_customers",
                action=action,
                resource_id=customers_resource.id,
                description=f"Разрешение на {action.value} клиентов"
            ))
        
        db.add_all(user_permissions + role_permissions + perm_permissions + 
                  product_permissions + order_permissions + customer_permissions)
        db.commit()
        
        # Создание тестовых пользователей
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@example.com",
            name="Администратор",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        
        manager_user = User(
            id=str(uuid.uuid4()),
            email="manager@example.com",
            name="Менеджер",
            hashed_password=get_password_hash("manager123"),
            is_active=True
        )
        
        test_user = User(
            id=str(uuid.uuid4()),
            email="user@example.com",
            name="Тестовый пользователь",
            hashed_password=get_password_hash("user123"),
            is_active=True
        )
        
        db.add_all([admin_user, manager_user, test_user])
        db.commit()
        
        # Назначение ролей пользователям
        admin_user_role = UserRole(
            id=str(uuid.uuid4()),
            user_id=admin_user.id,
            role_id=admin_role.id
        )
        
        manager_user_role = UserRole(
            id=str(uuid.uuid4()),
            user_id=manager_user.id,
            role_id=manager_role.id
        )
        
        test_user_role = UserRole(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            role_id=user_role.id
        )
        
        db.add_all([admin_user_role, manager_user_role, test_user_role])
        db.commit()
        
        # Назначение разрешений ролям (админ получает все разрешения)
        admin_role_permissions = []
        for permission in user_permissions + role_permissions + perm_permissions + \
                         product_permissions + order_permissions + customer_permissions:
            admin_role_permissions.append(RolePermission(
                id=str(uuid.uuid4()),
                role_id=admin_role.id,
                permission_id=permission.id
            ))
        
        # Менеджер получает разрешения на чтение и создание продуктов, заказов, клиентов
        manager_role_permissions = []
        for permission in product_permissions + order_permissions + customer_permissions:
            if permission.action in [ActionType.READ, ActionType.CREATE, ActionType.LIST]:
                manager_role_permissions.append(RolePermission(
                    id=str(uuid.uuid4()),
                    role_id=manager_role.id,
                    permission_id=permission.id
                ))
        
        # Обычный пользователь получает только разрешения на чтение
        user_role_permissions = []
        for permission in product_permissions + order_permissions + customer_permissions:
            if permission.action in [ActionType.READ, ActionType.LIST]:
                user_role_permissions.append(RolePermission(
                    id=str(uuid.uuid4()),
                    role_id=user_role.id,
                    permission_id=permission.id
                ))
        
        db.add_all(admin_role_permissions + manager_role_permissions + user_role_permissions)
        db.commit()
        
        print("Тестовые данные успешно созданы!")
        print(f"Администратор: admin@example.com / admin123")
        print(f"Менеджер: manager@example.com / manager123")
        print(f"Пользователь: user@example.com / user123")
        
    except Exception as e:
        print(f"Ошибка при создании тестовых данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_test_data()