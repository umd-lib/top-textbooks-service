FROM python:3.13.17-slim

EXPOSE 5000

WORKDIR /opt/alma-service

COPY . /opt/alma-service/

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt -e .

ENTRYPOINT ["alma-service", "--alma_config", "alma_config.yaml"]
