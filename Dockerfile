# 1. Используем официальный образ Python версии 3.12
FROM python:3.12

# 2. Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# 3. Копируем все файлы проекта в контейнер
COPY . .

# 4. Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5. Указываем команду для запуска бота
CMD ["python", "rmbg.py"]

