FROM python:3.7.11-stretch

WORKDIR /home/botbay

COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY . .

CMD ["make", "dockerrun"]