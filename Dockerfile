FROM python:3.14 AS build

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .

COPY scripts/entry.sh /
RUN chmod +x /entry.sh

ENTRYPOINT ["sh", "/entry.sh"]