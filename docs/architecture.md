# Архитектура Synonym Quest

## Слои
┌─────────────────────────────────────────────────────┐
│ handlers/ (план) — maxapi-роутеры │
│ ↓ вызывает │
│ services/ — бизнес-логика, async │
│ ↓ работает с │
│ models/ — SQLAlchemy ORM │
│ ↓ через │
│ database.py — engine, AsyncSessionLocal │
└─────────────────────────────────────────────────────┘
↑
states/ — FSM-состояния (StrEnum)

Правило: **сервисы не знают про maxapi**. Они принимают `AsyncSession`
снаружи, делают `flush()` и **не коммитят** — коммит на стороне хендлера
или вызывающего кода. Это позволяет переиспользовать сервисы в тестах,
скриптах и хендлерах одинаково.

## Модель данных

### `users`
- `user_id` (PK, BigInt) — приходит от MAX
- `role` — `student` / `teacher`
- `teacher_code` — у ученика это код его учителя, у учителя — его собственный код
- `current_rank`, `total_xp`, `total_tasks_completed`, `accuracy`

**Особенность**: `teacher_code` уникален **только среди учителей**.
Это реализовано частичным уникальным индексом:

```sql
CREATE UNIQUE INDEX ix_users_teacher_code_teacher
ON users (teacher_code) WHERE role = 'teacher';

У учеников teacher_code может повторяться (это код их класса).

tasks
task_id (PK)

title, full_text (с ___), correct_text

word_bank — массив слов, из которых надо выбирать

difficulty_level — 1..5 (не путать с механикой!)

task_type — механика: word_tyr / context_detective /
synonym_puzzle / synonym_battle / boss

is_boss_level — дублирует task_type='boss' для удобства фильтров

topic — тема (weather, business, ...)

Важно: difficulty_level и task_type — разные оси. Уровень
сложности (1..5) используется для подбора задания по силе ученика.
Механика (task_type) — для отчётов учителя и для того, в какое
FSM-состояние переводить пользователя.

task_steps
step_id, task_id, step_number (1-based), correct_word, context_hint

Уникальность (task_id, step_number) обеспечивается сервисом

sessions
session_id (PK)

user_id, task_id

status — in_progress / completed / abandoned

current_step — сколько шагов пройдено

remaining_words — массив, из которого убираются использованные

user_answers — JSONB: {"1": "word1", "2": "word2", ...}

is_correct — true, если все шаги верны (заполняется в complete)

score — накопленный XP внутри сессии

started_at, completed_at

teacher_reports
Модель есть, но пока не используется. Оставлена на будущее (кэш отчётов,
история). В MVP отчёты считаются на лету в TeacherService.

Ключевые решения
Почему task_type — Enum, а не строка
У task_type фиксированный набор значений, он участвует в отчётах
и FSM. Enum даёт валидацию на уровне БД и автодополнение в IDE.
Альтернатива (строка + CHECK) менее удобна.

Почему user_answers — JSONB, а не отдельная таблица
Ответы пишутся атомарно на шаг и потом читаются для подсчёта
correct_count при завершении. Отдельная таблица была бы overkill:
никогда не запрашиваем «все ответы на шаг X по всем сессиям» отдельным
SQL. Если такое понадобится (например, для аналитики по пропускам в
FR-06 из старого ТЗ) — пересмотрим.

Важно: JSONB-поле переприсваивается копией (dict(...)), потому
что SQLAlchemy не отслеживает in-place мутации JSONB без MutableDict.

Почему сервисы не коммитят
Тесты (db_session в conftest.py) оборачивают каждый тест в транзакцию
и откатывают её в конце. Если сервис коммитит — транзакция зафиксируется
раньше, и откат уже ничего не вернёт. Поэтому правило «flush, не commit».

Почему тестовая БД создаётся из Base.metadata, а не через alembic
Скорость. create_all за 200 мс против alembic upgrade head за секунды
с рестартами. Миграции тестируются отдельно (вручную перед коммитом
изменений в моделях).

Почему /random через ORDER BY random()
Postgres умеет ORDER BY random() LIMIT 1 быстро на маленьких таблицах.
При росте tasks до десятков тысяч — заменить на TABLESAMPLE или
случайный ID. Пока таблица маленькая, преждевременно.

Почему FSM-состояния — StrEnum, а не IntEnum
maxapi принимает state как строку. StrEnum даёт:

Прямую передачу state=WordTyr.ANSWERING (автоматически → строка)

Сравнение со строкой без явного преобразования

Читаемые значения в логах и БД ("word_tyr:answering" вместо 1)

Формат "<группа>:<подсостояние>" выбран, чтобы будущий переход
«прервать уровень → выйти в меню» был явным: группу можно сматчить
по префиксу.