FROM python:3.12

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/app

RUN mkdir tmp

EXPOSE 8080 

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
