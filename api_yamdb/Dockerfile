FROM python:3.7-slim
WORKDIR /app/api_yamdb
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .

CMD python manage.py runserver 0:5000