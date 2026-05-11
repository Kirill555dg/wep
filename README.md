# Web Education Platform (WEP)

LMS-система для управления учебным процессом: классы, уроки, домашние задания, тестирование и статистика.

## Назначение

WEP - веб-система для организации учебного процесса, в которой:

- **Преподаватель** управляет классами, уроками, домашними заданиями и базой задач, анализирует прогресс
- **Студент** вступает в классы, проходит уроки, выполняет домашние задания, видит личный прогресс
- Система предоставляет коммуникации (чат класса) и статистику

## Структура монорепозитория

```
wep/
├── backend/          # FastAPI backend
├── frontend/         # React + TypeScript frontend
├── deploy/           # Docker Compose
├── docs/             # Документация
├── tools/            # Вспомогательные скрипты
├── .gitignore
├── LICENSE
└── README.md
```

## Технологический стек

- **Backend**: Python 3.12+, FastAPI, PostgreSQL
- **Frontend**: TypeScript, React, Vite
- **Infrastructure**: Docker, Docker Compose

## Быстрый старт

```bash
git clone https://github.com/kerrodar/wep.git
cd wep

# Запустить инфраструктуру (PostgreSQL, Redis)
cd deploy
docker-compose up -d

# Backend и Frontend запускаются локально (см. соответствующие README)
```

## Разработка

См. README в соответствующих директориях:
- [Backend](backend/README.md)
- [Frontend](frontend/README.md)

## Архитектура

- **Backend**: Clean Architecture
- **Frontend**: Feature-Sliced Design
- **API**: REST + WebSocket

## Лицензия

MIT License - см. [LICENSE](LICENSE)

## Автор

Кирилл Миркин (ИКБО-10-23, РТУ МИРЭА)
