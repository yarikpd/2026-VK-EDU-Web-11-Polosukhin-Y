FROM python:3.14 AS build

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .

RUN chmod +x ./scripts/entry.sh

ENTRYPOINT ["sh", "./scripts/entry.sh"]