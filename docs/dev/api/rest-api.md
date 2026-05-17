# REST API документация

Описание REST API endpoints Web Education Platform.

## Базовый URL

- Development: `http://localhost:8023/api/v1`
- Production: `https://api.wep.example.com/api/v1`

## Аутентификация

Используется JWT Bearer токен в заголовке:

```
Authorization: Bearer <token>
```

## Общие правила

### Пагинация

Параметры:
- `skip` - смещение (по умолчанию 0)
- `limit` - количество (по умолчанию 50, максимум 100)

Ответ:
```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

### Формат ошибок

```json
{
  "error": {
    "code": "not_found",
    "message": "Resource not found",
    "meta": {}
  },
  "request_id": "uuid"
}
```

## Endpoints

### Authentication (`/auth`)

#### POST `/auth/register`
Регистрация нового пользователя

Request:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "student"
}
```

Response:
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "student"
  }
}
```

#### POST `/auth/login`
Вход в систему

Request:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### POST `/auth/switch-role`
Смена активной роли

Request:
```json
{
  "role": "teacher"
}
```

### Classrooms (`/classrooms`)

#### GET `/classrooms`
Список классов (для teacher - свои, для student - присоединенные)

#### POST `/classrooms`
Создание класса (teacher only)

Request:
```json
{
  "name": "Математика 10А",
  "description": "Класс по математике"
}
```

#### GET `/classrooms/{id}`
Получение класса

#### PUT `/classrooms/{id}`
Обновление класса (teacher only)

#### POST `/classrooms/join`
Присоединение к классу (student only)

Request:
```json
{
  "invite_code": "ABC123"
}
```

#### GET `/classrooms/{id}/students`
Список студентов класса

### Lessons (`/lessons`)

#### GET `/classrooms/{classroom_id}/lessons`
Список уроков класса

#### POST `/lessons`
Создание урока (teacher only)

Request:
```json
{
  "classroom_id": "uuid",
  "title": "Введение в алгебру",
  "description": "Первый урок",
  "order": 1,
  "is_published": false
}
```

#### GET `/lessons/{id}`
Получение урока

#### PUT `/lessons/{id}`
Обновление урока (teacher only)

### Homework (`/homework`)

#### GET `/lessons/{lesson_id}/homework`
Список ДЗ урока

#### POST `/homework`
Создание ДЗ (teacher only)

Request:
```json
{
  "lesson_id": "uuid",
  "title": "ДЗ №1",
  "description": "Задачи по теме",
  "deadline": "2026-05-20T23:59:59Z",
  "is_published": false,
  "problems": [
    {
      "problem_id": "uuid",
      "points": 5,
      "order": 1
    }
  ]
}
```

#### GET `/homework/{id}`
Получение ДЗ

#### GET `/homework/{id}/problems`
Список задач ДЗ (для student - без правильных ответов)

### Testing (`/testing`)

#### POST `/testing/submit-answer`
Отправка ответа на задачу (student only)

Request:
```json
{
  "homework_id": "uuid",
  "problem_id": "uuid",
  "answer": "42"
}
```

#### POST `/testing/homework/{id}/submit`
Финальная отправка ДЗ (student only)

### Statistics (`/statistics`)

#### GET `/statistics/me`
Личная статистика студента

#### GET `/statistics/me/progress`
Прогресс студента по всем классам

#### GET `/statistics/homework/{homework_id}`
Статистика по ДЗ (teacher only)

#### GET `/statistics/classroom/{classroom_id}/progress`
Прогресс класса (teacher only)

#### GET `/statistics/student/{student_id}`
Статистика студента (teacher only)

### Chat (`/classrooms/{id}/chat`)

#### GET `/classrooms/{id}/chat/messages`
История сообщений чата

#### POST `/classrooms/{id}/chat/messages`
Отправка сообщения

Request:
```json
{
  "content": "Привет всем!"
}
```

#### WS `/classrooms/{id}/chat/ws`
WebSocket endpoint для realtime чата

## Swagger UI

Полная интерактивная документация доступна на `/api/docs`
