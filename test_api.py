import requests
import json

# Базовый URL API
BASE_URL = "http://localhost:8000/api"

def test_authentication():
    """Тестирование аутентификации"""
    print("=== ТЕСТИРОВАНИЕ АУТЕНТИФИКАЦИИ ===")
    
    # Тест регистрации
    print("\n1. Регистрация нового пользователя:")
    register_data = {
        "email": "test@example.com",
        "name": "Тестовый пользователь",
        "password": "test123",
        "password_confirm": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Тест входа
    print("\n2. Вход в систему:")
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"Токен получен: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print(f"Ошибка входа: {response.json()}")
            return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def test_protected_endpoints(token):
    """Тестирование защищенных эндпоинтов"""
    if not token:
        print("Нет токена для тестирования защищенных эндпоинтов")
        return
    
    print("\n=== ТЕСТИРОВАНИЕ ЗАЩИЩЕННЫХ ЭНДПОИНТОВ ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Тест получения профиля
    print("\n1. Получение профиля пользователя:")
    try:
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            profile = response.json()
            print(f"Профиль: {profile['name']} ({profile['email']})")
        else:
            print(f"Ошибка: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Тест получения продуктов (бизнес-объекты)
    print("\n2. Получение списка продуктов:")
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"Найдено продуктов: {len(products)}")
            for product in products[:3]:  # Показываем первые 3
                print(f"  - {product['name']}: {product['price']} руб.")
        else:
            print(f"Ошибка: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Тест получения заказов
    print("\n3. Получение списка заказов:")
    try:
        response = requests.get(f"{BASE_URL}/orders", headers=headers)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            orders = response.json()
            print(f"Найдено заказов: {len(orders)}")
            for order in orders[:3]:  # Показываем первые 3
                print(f"  - Заказ {order['id']}: {order['customer']} - {order['total']} руб.")
        else:
            print(f"Ошибка: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Тест получения клиентов
    print("\n4. Получение списка клиентов:")
    try:
        response = requests.get(f"{BASE_URL}/customers", headers=headers)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            customers = response.json()
            print(f"Найдено клиентов: {len(customers)}")
            for customer in customers[:3]:  # Показываем первые 3
                print(f"  - {customer['name']}: {customer['email']}")
        else:
            print(f"Ошибка: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")

def test_permission_management(token):
    """Тестирование управления разрешениями"""
    if not token:
        print("Нет токена для тестирования управления разрешениями")
        return
    
    print("\n=== ТЕСТИРОВАНИЕ УПРАВЛЕНИЯ РАЗРЕШЕНИЯМИ ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Тест получения ролей
    print("\n1. Получение списка ролей:")
    try:
        response = requests.get(f"{BASE_URL}/roles", headers=headers)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            roles = response.json()
            print(f"Найдено ролей: {len(roles)}")
            for role in roles:
                print(f"  - {role['name']}: {role['description']}")
        else:
            print(f"Ошибка: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Тест получения ресурсов
    print("\n2. Получение списка ресурсов:")
    try:
        response = requests.get(f"{BASE_URL}/resources", headers=headers)
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            resources = response.json()
            print(f"Найдено ресурсов: {len(resources)}")
            for resource in resources:
                print(f"  - {resource['name']}: {resource['description']}")
        else:
            print(f"Ошибка: {response.json()}")
    except Exception as e:
        print(f"Ошибка: {e}")

def test_unauthorized_access():
    """Тестирование доступа без авторизации"""
    print("\n=== ТЕСТИРОВАНИЕ ДОСТУПА БЕЗ АВТОРИЗАЦИИ ===")
    
    # Попытка доступа к защищенному эндпоинту без токена
    print("\n1. Попытка доступа к профилю без токена:")
    try:
        response = requests.get(f"{BASE_URL}/profile")
        print(f"Статус: {response.status_code}")
        if response.status_code == 401:
            print("✓ Правильно: доступ запрещен (401 Unauthorized)")
        else:
            print(f"✗ Неожиданный статус: {response.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    # Попытка доступа к бизнес-объектам без токена
    print("\n2. Попытка доступа к продуктам без токена:")
    try:
        response = requests.get(f"{BASE_URL}/products")
        print(f"Статус: {response.status_code}")
        if response.status_code == 401:
            print("✓ Правильно: доступ запрещен (401 Unauthorized)")
        else:
            print(f"✗ Неожиданный статус: {response.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ СИСТЕМЫ АУТЕНТИФИКАЦИИ И АВТОРИЗАЦИИ")
    print("=" * 60)
    
    # Тест доступа без авторизации
    test_unauthorized_access()
    
    # Тест аутентификации
    token = test_authentication()
    
    # Тест защищенных эндпоинтов
    test_protected_endpoints(token)
    
    # Тест управления разрешениями
    test_permission_management(token)
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("\nДля запуска приложения выполните: python main.py")
    print("API документация доступна по адресу: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 