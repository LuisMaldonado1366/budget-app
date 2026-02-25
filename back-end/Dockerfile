
FROM python:3.11.9

RUN apt-get update && apt-get -y install cron vim

WORKDIR /usr/src/app/

RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /usr/src/app/

CMD ["python", "-u", "/usr/src/app/main.py"]