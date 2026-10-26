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

## Администрирование

### Сменить учителя ученику

Ученик сам не может сменить или сбросить учителя (защита от
перепривязки). Делается через SQL:

\`\`\`sql
-- отвязать от учителя
UPDATE users SET teacher_code = NULL WHERE user_id = <student_id>;

-- привязать к другому учителю
UPDATE users SET teacher_code = '<новый_код>' WHERE user_id = <student_id>;
\`\`\`

### Вернуть учителя в ученика

\`\`\`sql
UPDATE users SET role = 'student', teacher_code = NULL
WHERE user_id = <user_id>;
\`\`\`

### Бот в MAX

[@ideya_fiks_19_bot](https://max.ru/ideya_fiks_19_bot)

## Сценарий использования

1. **Учитель** открывает бота, отправляет `/start` → `/teacher`.
   Бот повышает роль и выдаёт 8-символьный код (например, `IBP1FEF5`).
2. **Ученик** открывает бота, отправляет `/start` → `/student IBP1FEF5`.
   Бот привязывает ученика к учителю.
3. **Ученик** выбирает механику (`/word_tyr`, `/context_detective`,
   `/synonym_puzzle`, `/synonym_battle`, `/boss`), проходит задание,
   получает XP и растёт в ранге.
4. **Учитель** открывает `/my_students`, `/class_stats`, `/weak_tasks`
   и видит прогресс класса.

## Команды

### Ученик
| Команда | Что делает |
|---|---|
| `/start` | Регистрация, меню |
| `/help` | Справка |
| `/role` | Текущая роль, XP, ранг |
| `/student` | Стать учеником |
| `/student <КОД>` | Привязаться к учителю |
| `/word_tyr` | Механика «Словесный тир» |
| `/context_detective` | Механика «Детектив контекста» |
| `/synonym_puzzle` | Механика «Синонимический пазл» |
| `/synonym_battle` | Механика «Битва синонимов» |
| `/boss` | Boss-уровень |
| `/cancel` | Прервать текущее задание |

### Учитель
| Команда | Что делает |
|---|---|
| `/teacher` | Стать учителем / открыть кабинет |
| `/my_students` | Список учеников |
| `/class_stats` | Статистика класса по механикам |
| `/weak_tasks` | Меню слабых заданий |
| `/weak_tasks <task_type>` | Слабые задания в категории |

## Администрирование

Ученик сам не может сменить или сбросить учителя (защита от перепривязки).
Все операции — через SQL:

### Отвязать ученика от учителя

```sql
UPDATE users SET teacher_code = NULL WHERE user_id = <student_id>;
```

### Привязать к другому учителю

```sql
UPDATE users SET teacher_code = '<новый_код>' WHERE user_id = <student_id>;
```

### Вернуть учителя в ученика

```sql
UPDATE users SET role = 'student', teacher_code = NULL
WHERE user_id = <user_id>;
```

### Найти учителя по коду

```sql
SELECT user_id, display_name FROM users
WHERE role = 'teacher' AND teacher_code = '<код>';
```

### Все ученики учителя

```sql
SELECT u.user_id, u.display_name, u.total_xp, u.current_rank
FROM users u
JOIN users t ON t.teacher_code = u.teacher_code
WHERE t.user_id = <teacher_id> AND u.role = 'student';
```

Выполнять через:

```powershell
docker exec -it sq_postgres psql -U user -d synonym_quest -c "SQL..."
```

## XP и ранги

- **+10 XP** за каждый правильный шаг задания.
- **+20 XP** бонус, если все шаги решены без ошибок.
- Ранги (по суммарному XP): `novice` (0), `apprentice` (100),
  `wordsmith` (300), `linguist` (700), `master` (1500),
  `grandmaster` (3000).
