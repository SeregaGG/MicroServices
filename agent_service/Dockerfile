FROM python:3.12.5


WORKDIR /agent_service


COPY ./requirements.txt /agent_service/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /agent_service/requirements.txt


COPY . /agent_service


CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]