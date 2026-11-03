# Используем официальный образ Python (slim-версия легче)
FROM python:3.12-slim

# Отключаем буферизацию вывода Python (чтобы логи сразу шли в консоль)
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Сначала копируем только requirements, чтобы Docker кэшировал установку библиотек
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта внутрь контейнера
COPY . .

# Добавляем папку src в PYTHONPATH, чтобы работал запуск `python -m synonym_quest.bot`
ENV PYTHONPATH=/app/src

# Команда для запуска бота
CMD ["python", "-m", "synonym_quest.bot"]