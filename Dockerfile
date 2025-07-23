# Используем официальный образ Python 3.12 (или 3.11-slim)
FROM python:3.12-slim

# Устанавливаем системные зависимости, в том числе для PyCryptodome (MD4)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /app

# Копируем список зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install "urllib3<1.27" --no-cache-dir -r requirements.txt 
# Копируем исходники бота и .env
COPY .env .
COPY bot.py .

# Указываем точку входа
CMD ["python", "bot.py"]
