FROM python:3.12.5


WORKDIR /user_service


COPY ./requirements.txt /user_service/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /user_service/requirements.txt


COPY . /user_service


CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]