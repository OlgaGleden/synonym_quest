# Synonym Quest

Чат-бот для изучения английских синонимов в мессенджере **MAX**.
Целевая аудитория — старшеклассники и преподаватели.

Бот в MAX: [@ideya_fiks_19_bot](https://max.ru/ideya_fiks_19_bot)

## Механики

Пять категорий заданий (`Task.task_type`):

| Код                 | Название             | Описание |
|---------------------|----------------------|----------|
| `word_tyr`          | Словесный тир        | Выбор правильного слова из банка |
| `context_detective` | Детектив контекста   | Понимание смысла по контексту |
| `synonym_puzzle`    | Синонимический пазл  | Сборка предложения из синонимов |
| `synonym_battle`    | Битва синонимов      | Быстрый выбор подходящего оттенка |
| `boss`              | Boss-уровень         | Сложные комплексные задания |

Прогресс ученика: XP, ранги, точность. Кабинет учителя — аналитика по классу и по каждому ученику.

## Стек

- **Python 3.14+** (управление зависимостями через `uv`)
- **SQLAlchemy 2.x (async)** + `asyncpg` + **PostgreSQL 15**
- **Alembic** (миграции БД)
- **Redis 7** (зарезервирован для кэша/очередей)
- **maxapi 1.2.2** (клиент MAX)
- **pydantic-settings** (конфиг)
- **pytest** + `pytest-asyncio` (120+ тестов)

## Быстрый старт

### 1. Клонировать и поставить зависимости

```powershell
cd C:\max\synonym_quest
python -m venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -e .

2. Запустить инфраструктуру (БД)
powershell
docker compose -f docker-compose.dev.yml up -d
(Поднимутся контейнеры sq_postgres и sq_redis)

3. Настроить .env
Файл .env не хранится в git (см. .gitignore) — в репозитории лежит только образец .env.example. Скопируйте его и заполните:

powershell
Copy-Item .env.example .env
Обязательно укажите ваш BOT_TOKEN (получить у @MasterBot в MAX).

4. Применить миграции и залить задания
powershell
alembic upgrade head
python scripts/seed_tasks.py
5. Запустить бота
powershell
python -m synonym_quest.bot
Сценарий использования
Учитель открывает бота, отправляет /start → /teacher.
Бот повышает роль и выдаёт 8-символьный код (например, IBP1FEF5).

Ученик открывает бота, отправляет /start → /student IBP1FEF5.
Бот привязывает ученика к учителю.

Ученик выбирает механику (/word_tyr, /context_detective, /synonym_puzzle, /synonym_battle, /boss), проходит задание, получает XP и растёт в ранге.

Учитель открывает /my_students, /class_stats, /weak_tasks и видит прогресс класса.

Команды
Ученик
Команда	Что делает
/start	Регистрация, главное меню
/help	Справка по командам
/role	Текущая роль, XP, ранг
/student	Стать учеником
/student <КОД>	Привязаться к учителю
/word_tyr	Механика «Словесный тир»
/context_detective	Механика «Детектив контекста»
/synonym_puzzle	Механика «Синонимический пазл»
/synonym_battle	Механика «Битва синонимов»
/boss	Boss-уровень
/cancel	Прервать текущее задание
Учитель
Команда	Что делает
/teacher	Стать учителем / открыть кабинет
/my_students	Список учеников (ранг, XP, точность)
/class_stats	Статистика класса по механикам
/weak_tasks	Меню слабых заданий
/weak_tasks <task_type>	Слабые задания в конкретной категории
XP и ранги
+10 XP за каждый правильный шаг задания.

+20 XP бонус, если все шаги решены без ошибок.

Ранги (по суммарному XP):

novice (0)

apprentice (100)

wordsmith (300)

linguist (700)

master (1500)

grandmaster (3000)

Администрирование
Ученик сам не может сменить или сбросить учителя (защита от перепривязки). Все операции выполняются через SQL-запросы к базе данных.

Выполнять через:

powershell
docker exec -it sq_postgres psql -U user -d synonym_quest -c "SQL..."
Отвязать ученика от учителя
sql
UPDATE users SET teacher_code = NULL WHERE user_id = <student_id>;
Привязать к другому учителю
sql
UPDATE users SET teacher_code = '<новый_код>' WHERE user_id = <student_id>;
Вернуть учителя в ученика
sql
UPDATE users SET role = 'student', teacher_code = NULL
WHERE user_id = <user_id>;
Найти учителя по коду
sql
SELECT user_id, display_name FROM users
WHERE role = 'teacher' AND teacher_code = '<код>';
Все ученики учителя
sql
SELECT u.user_id, u.display_name, u.total_xp, u.current_rank
FROM users u
JOIN users t ON t.teacher_code = u.teacher_code
WHERE t.user_id = <teacher_id> AND u.role = 'student';
Структура проекта
text
src/synonym_quest/
├── bot.py            # Точка входа, graceful shutdown
├── config.py         # Настройки (pydantic-settings)
├── database.py       # Подключение к БД, сессии
├── models/           # SQLAlchemy модели (User, Task, Session)
├── services/         # Бизнес-логика (User, Task, Session, Teacher)
├── handlers/         # Роутеры maxapi (start, registration, levels, teacher)
├── states/           # FSM-состояния
└── seed_data.py      # 20 заданий для наполнения БД