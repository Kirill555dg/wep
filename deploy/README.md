# WEP Deploy

Docker Compose для инфраструктурных сервисов (PostgreSQL, MinIO).

Подробнее: [docs/dev/](../docs/dev/)

## Быстрый старт

```bash
cp .env.example .env
docker compose up -d
```

## Сервисы

| Сервис | Порт (хост) | Назначение |
|---|---|---|
| PostgreSQL | 5433 | База данных |
| MinIO S3 | 9000 | Объектное хранилище |
| MinIO Console | 9001 | Web-интерфейс MinIO |

## Остановка

```bash
docker compose down
docker compose down -v   # с удалением volumes
```
