FROM python:3.12-slim

EXPOSE 5000

WORKDIR /opt/top-textbooks-service

COPY requirements.txt src pyproject.toml /opt/top-textbooks-service/

RUN pip install -r requirements.txt -e .

ENTRYPOINT ["top-textbooks-service"]
