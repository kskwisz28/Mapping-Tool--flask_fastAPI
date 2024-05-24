FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app/tsi/requirements.txt /app/requirements.txt

RUN pip install pip --upgrade
RUN pip install -r /app/requirements.txt

COPY ./app/tsi /app
