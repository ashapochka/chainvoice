FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV PYTHONPATH=/
COPY ./app /app
COPY ./requirements.txt /requirements.txt
RUN pip install -U pip
RUN pip install -r /requirements.txt
