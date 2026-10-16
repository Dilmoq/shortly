# shortly — сервис сокращения ссылок

REST API для создания коротких ссылок, перенаправления по ним и отслеживания статистики переходов.
Написано на Python (FastAPI) с использованием SQLite через SQLAlchemy ORM.

## Возможности

- Сокращение ссылок: POST-запрос возвращает уникальный короткий код (случайный, URL-safe)
- Редирект по короткой ссылке с учётом кликов
- Статистика по каждой ссылке: количество переходов и время создания
- Валидация входных URL (только http/https, защита от XSS и header-инъекций)
- Документация API формируется автоматически (`/docs`, Swagger UI)
- Не содержит секретов, легко разворачивается через Docker

## Технологии

| Компонент | Инструмент |
|---|---|
| HTTP API | FastAPI + Uvicorn |
| БД | SQLite + SQLAlchemy 2.x |
| Валидация схем | Pydantic 2 |
| Тесты | pytest + httpx (TestClient) |
| Линтер | ruff |
| CI | GitHub Actions (3 версии Python, линтер + тесты) |
| Деплой | Docker / docker-compose |

## Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Открыть: http://localhost:8000/docs

## Тесты

```bash
pip install -r requirements-dev.txt
pytest tests -v
```

Все эндпоинты и бизнес-логика покрыты тестами: генерация коротких кодов (base62),
валидация URL, сценарии API, подсчёт кликов, обработка ошибок 404/422.

## Примеры использования API

Создать короткую ссылку:

```bash
curl -X POST http://localhost:8000/api/links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/"}'
```

Ответ `201Created`:

```json
{
  "code": "2wqGwM",
  "url": "https://github.com/",
  "short_url": "http://localhost:8000/2wqGwM",
  "clicks": 0
}
```

Перейти по ссылке (браузер или curl):

```bash
curl -i http://localhost:8000/2wqGwM
# HTTP/1.1 302 Found
# Location: https://github.com/
```

Получить статистику:

```bash
curl http://localhost:8000/api/links/2wqGwM/stats
```

```json
{
  "code": "2wqGwM",
  "url": "https://github.com/",
  "clicks": 5,
  "created_at": "2026-10-16T12:00:00"
}
```

## Настройка (переменные окружения)

| Переменная | Значение по умолчанию | Описание |
|---|---|---|
| `SHORTLY_BASE_URL` | `http://localhost:8000/` | Публичный URL сервиса для формирования short_url |
| `SHORTLY_DATABASE_URL` | `sqlite:///./shortly.db` | SQLAlchemy URL БД (можно заменить на PostgreSQL) |
| `SHORTLY_CODE_LENGTH` | `6` | Длина генерируемого короткого кода |

## Деплой на сервер (Docker)

```bash
git clone https://github.com/<you>/shortly.git && cd shortly
docker compose up -d -e SHORTLY_BASE_URL=https://links.example.com/
```

БД хранится в томе `shortly-data`, поэтому данные переживают перезапуск контейнера.
Рекомендуется поставить nginx перед контейнером как reverse-proxy (пример конфигурации в `docs/` для будущих версий).

## Структура проекта

```
shortly/
├── app/
│   ├── main.py            # фабрика приложения, роутинг
│   ├── config.py          # настройки из env
│   ├── database.py        # engine, сессии, init_db
│   ├── models.py          # ORM-модель Link
│   ├── schemas.py         # валидация запросов/ответов (Pydantic)
│   ├── services.py        # бизнес-логика: base62, генерация кодов, валидация URL
│   └── routers/
│       ├── links.py       # POST /api/links, GET /api/links/{code}/stats
│       └── redirect.py    # GET /{code} — редирект на target
├── tests/
│   ├── conftest.py        # фикстуры с тестовой БД
│   ├── test_services.py   # юнит-тесты бизнес-логики
│   └── test_api.py        # е2е-тесты API
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .github/workflows/ci.yml
```
## Лицензия

MIT — см. [LICENSE](LICENSE).
