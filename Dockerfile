FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--log-file=-", "--log-level=debug", "run:app"] # for production