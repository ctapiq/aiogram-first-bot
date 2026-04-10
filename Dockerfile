# Берем официальный образ Python
FROM python:3.11-slim

# Принудительно устанавливаем poppler (тот самый pdfinfo, которого нам не хватает)
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*

# Создаем рабочую папку
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код бота
COPY . .

# Команда для запуска
CMD ["python", "main.py"]