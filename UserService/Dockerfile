FROM python:3.12.5


WORKDIR /UserService


COPY ./requirements.txt /UserService/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /UserService/requirements.txt


COPY . /UserService


CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]