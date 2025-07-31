# Инструкции по запуску и тестированию

## Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Инициализация базы данных
```bash
python init_data.py
```

### 3. Запуск приложения
```bash
python main.py
```

Приложение будет доступно по адресу: http://localhost:8000

## Тестирование системы

### Автоматическое тестирование
```bash
python test_api.py
```

### Ручное тестирование через API

#### 1. Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "name": "Новый пользователь",
    "password": "password123",
    "password_confirm": "password123"
  }'
```

#### 2. Вход в систему
```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

#### 3. Доступ к защищенным ресурсам
```bash
# Получение профиля
curl -X GET "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Получение списка продуктов
curl -X GET "http://localhost:8000/api/products" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Получение списка заказов
curl -X GET "http://localhost:8000/api/orders" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Тестовые пользователи

После инициализации создаются следующие пользователи:

| Email | Пароль | Роль | Права |
|-------|--------|------|-------|
| admin@example.com | admin123 | Администратор | Полный доступ ко всем ресурсам |
| manager@example.com | manager123 | Менеджер | Чтение и создание продуктов, заказов, клиентов |
| user@example.com | user123 | Пользователь | Только чтение продуктов, заказов, клиентов |

## API Документация

После запуска приложения доступна автоматическая документация:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Структура API

### Аутентификация
- `POST /api/register` - Регистрация
- `POST /api/login` - Вход в систему
- `POST /api/logout` - Выход из системы
- `GET /api/profile` - Получение профиля
- `PUT /api/profile` - Обновление профиля
- `DELETE /api/profile` - Удаление аккаунта

### Управление разрешениями
- `GET /api/roles` - Список ролей
- `POST /api/roles` - Создание роли
- `GET /api/resources` - Список ресурсов
- `POST /api/resources` - Создание ресурса
- `GET /api/permissions` - Список разрешений
- `POST /api/permissions` - Создание разрешения

### Бизнес-объекты
- `GET /api/products` - Список продуктов
- `GET /api/products/{id}` - Детали продукта
- `GET /api/orders` - Список заказов
- `GET /api/orders/{id}` - Детали заказа
- `GET /api/customers` - Список клиентов
- `GET /api/customers/{id}` - Детали клиента

## Проверка безопасности

### Тест 1: Доступ без авторизации
```bash
curl -X GET "http://localhost:8000/api/profile"
```
**Ожидаемый результат**: 401 Unauthorized

### Тест 2: Доступ с недействительным токеном
```bash
curl -X GET "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer invalid_token"
```
**Ожидаемый результат**: 401 Unauthorized

### Тест 3: Доступ с действительным токеном
```bash
# Сначала получите токен через login
curl -X GET "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer YOUR_VALID_TOKEN"
```
**Ожидаемый результат**: 200 OK с данными профиля

## Устранение неполадок

### Ошибка "email-validator is not installed"
```bash
pip install email-validator
```

### Ошибка "bcrypt version"
Это предупреждение не критично и не влияет на работу системы.

### Ошибка подключения к базе данных
Убедитесь, что файл базы данных создан:
```bash
python init_data.py
```

### Порт 8000 занят
Измените порт в файле `main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

## Демонстрация работы системы

1. **Запустите приложение**: `python main.py`
2. **Откройте браузер**: http://localhost:8000/docs
3. **Протестируйте API** через Swagger UI
4. **Запустите автоматические тесты**: `python test_api.py`

Система демонстрирует:
- ✅ Собственную аутентификацию (не использует встроенные возможности FastAPI)
- ✅ Гибкую систему разрешений (роли + прямые разрешения)
- ✅ Защиту ресурсов (401/403 ошибки)
- ✅ Mock бизнес-объекты для демонстрации
- ✅ Полную API документацию 