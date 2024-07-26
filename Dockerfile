FROM python:3.12-slim

EXPOSE 5000

WORKDIR /opt/alma-service

COPY . /opt/alma-service/

RUN pip install -r requirements.txt -e .

ENTRYPOINT ["alma-service"]
