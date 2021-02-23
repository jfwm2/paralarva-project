ARG PYTHON_VERSION=3.9.1

FROM python:${PYTHON_VERSION}
COPY requirements.txt .
RUN pip install -v --user -r requirements.txt
RUN mkdir -p /opt/paralarva
WORKDIR /opt/paralarva

COPY ./src .
COPY ./main.py .
COPY ./config.yaml .

CMD ["python3", "./main.py", "--listen-all-addr", "--log-level", "debug", "--dry-run"]
