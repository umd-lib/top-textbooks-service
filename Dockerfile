FROM python:3.12-slim

EXPOSE 5000

WORKDIR /opt/top-textbooks-service

COPY . /opt/top-textbooks-service/

RUN pip install -r requirements.txt -e .

ENTRYPOINT ["top-textbooks-service"]
