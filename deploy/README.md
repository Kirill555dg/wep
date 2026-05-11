# WEP Deploy

Docker Compose конфигурация для инфраструктуры Web Education Platform.

## Запуск

```bash
cp .env.example .env
# Отредактировать .env

docker-compose up -d
```

## Сервисы

- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Остановка

```bash
docker-compose down

# С удалением volumes
docker-compose down -v
```

## Примечание

Backend и Frontend запускаются локально для разработки.
Схема production деплоя будет спроектирована отдельно.
