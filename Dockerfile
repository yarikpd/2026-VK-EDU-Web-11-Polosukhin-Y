FROM python:3.14 AS development

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /app
ENTRYPOINT ["sh", "./scripts/entry.sh"]

FROM development AS standalone
COPY . .
