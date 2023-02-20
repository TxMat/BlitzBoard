FROM python:latest

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . /app
WORKDIR /app

ENTRYPOINT ["gunicorn", "client:app", "-w", "1", "-b", "0.0.0.0:80"]
# ENTRYPOINT ["python", "Client.py"]