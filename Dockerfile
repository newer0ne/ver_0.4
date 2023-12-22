FROM python:3.10.0

# Директорию внутри контейнера, где будет размещено приложение
WORKDIR /app

# Копирование файлов в контейнер
COPY nensi.py /app/nensi.py
COPY requirements.txt /app/requirements.txt

# Зависимости приложения
RUN pip install -r requirements.txt

# Укажите команду, которая будет запускать ваше приложение внутри контейнера
CMD ["streamlit", "run", "--server.port", "8503", "./nensi.py", "[ARGUMENTS]"]