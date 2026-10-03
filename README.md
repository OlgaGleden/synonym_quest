# Synonym Quest

Чат-бот для изучения английских синонимов в мессенджере **MAX**.
Целевая аудитория — старшеклассники и преподаватели.

## Механики

Пять категорий заданий (`Task.task_type`):

| Код                 | Название             |
|---------------------|----------------------|
| `word_tyr`          | Словесный тир        |
| `context_detective` | Детектив контекста   |
| `synonym_puzzle`    | Синонимический пазл  |
| `synonym_battle`    | Битва синонимов      |
| `boss`              | Boss-уровень         |

Прогресс ученика: XP, ранги, точность. Кабинет учителя — аналитика
по классу и по каждому ученику.

## Стек

- Python 3.12+ (проект собирается на 3.14)
- SQLAlchemy 2.x (async) + asyncpg + PostgreSQL 15
- Alembic (миграции)
- Redis 7 (зарезервирован)
- maxapi 1.2.2 (клиент MAX)
- pydantic-settings (конфиг)
- pytest + pytest-asyncio (тесты)

## Быстрый старт

### 1. Клонировать и поставить зависимости

```powershell
cd C:\max\synonym_quest
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

### 3. Настроить `.env`

Файл `.env` не хранится в git (см. `.gitignore`) — в репозитории лежит только образец `.env.example`. Скопируй его:
```powershell
Copy-Item .env.example .env