# WEP Deploy

Docker Compose конфигурация для развертывания Web Education Platform.

## Запуск

```bash
cp .env.example .env
# Отредактировать .env

docker-compose up -d
```

## Сервисы

- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Backend API**: http://localhost:8023
- **Frontend**: http://localhost:80

## Остановка

```bash
docker-compose down

# С удалением volumes
docker-compose down -v
```
