# WEP Tools

Утилиты для разработки и эксплуатации.

## Health Checker

CLI-утилита проверки инфраструктуры (PostgreSQL, MinIO, миграции, API).

```bash
cd health_checker
./build.sh                          # собрать standalone-бинарник
./dist/health-checker               # запустить бинарник
uv run python -m health_checker     # запустить через uv
```

Подробнее: [docs/dev/tools/](../docs/dev/tools/)
