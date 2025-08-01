import io
import uuid
from datetime import date
from typing import Optional, Tuple

from fastapi import APIRouter, File, UploadFile, HTTPException, Response, Cookie
from pydub import AudioSegment
import speech_recognition as sr

import google_auth_oauthlib.flow

from langchain_gigachat.chat_models import GigaChat
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_gigachat.tools.giga_tool import giga_tool
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/userinfo.email']

router = APIRouter(prefix="/vacation_agent", tags=["Actions"])

load_dotenv()


giga = GigaChat(
    model="GigaChat",
    verify_ssl_certs=False,
    credentials=os.getenv('GIGA_KEY')
)

local_storage = dict()

class Vacation(BaseModel):
    start_date: str = Field(description='Начало отпуска строго в формате d.m.y')
    end_date: str = Field(description='Конец оптуска строго в формате d.m.y')

class ParseResult(BaseModel):
    """
    Схема для распаршеных дат
    """
    start_date: date = Field(description='Начало отпуска')
    end_date: date = Field(description='Конец оптуска')


few_shot_examples = [
    {
        "request": "Хочу в отпуск с 13 по 25 мая",
        "params": {"start_date": '13.08.2025', "end_date": '25.08.2025'},
    }
]
@giga_tool(few_shot_examples=few_shot_examples, response_format="content_and_artifact")
def parse_date_from_string(
    vacation: Vacation
) -> Tuple[str, ParseResult]:
    """
    Функция для парсинга даты начала отпуска и даты конца отпуска
    Args:
        vacation: даты всегда в формате d.m.y - если чего-то не хватает, то ставятся заглушки
    """

    start_day, start_month, start_year = vacation.start_date.split('.')
    end_day, end_month, end_year = vacation.end_date.split('.')

    try:
        start_year = int(start_year)
        end_year = int(end_year)
    except ValueError:
        start_year = 2025
        end_year = 2025
    start_date = date(start_year, int(start_month), int(start_day))
    end_date = date(end_year, int(end_month), int(end_day))
    return "Обработано", ParseResult(start_date=start_date, end_date=end_date)


functions = [parse_date_from_string]
giga_with_functions = giga.bind_functions(functions)
agent_executor = create_react_agent(giga_with_functions,
                                    functions,
                                    checkpointer=MemorySaver(), recursion_limit=100,
                                    prompt="Ты бот для оформления отпусков. "
                                           "Твоя основная задача узнать у пользователя даты отпуска и представить их в формат d.m.y - ты должен всегда строго соблюдать такой формат! "
                                           "Если нет части, то забивай их заглушками - например 01.07.y"
                                           "Если год не указан, то попроси уточнить.",
                                    response_format=ParseResult)

@router.post("/authorize")
async def authorize(response: Response):
    thread_id = uuid.uuid4().hex
    config = {"configurable": {"thread_id": thread_id}}
    agent_executor.invoke({"messages": [HumanMessage(content='Привет!')]}, config=config)
    response.set_cookie(key='thread_id', value=thread_id, httponly=True)
    local_storage[thread_id] = None
    return { "thread_id": thread_id }

@router.post("/oauth2")
async def oauth2(response: Response):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = 'http://vacation.1429773-ct12216.tw1.ru/authorize'

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    return { "authorization_url": authorization_url }


@router.post("/voice_message_upload")
async def upload_audio_file(audio_file: UploadFile = File(...), thread_id: Optional[str] = Cookie(None)):

    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Не верный тип файла. Загрузите аудио файл.")
    try:
        audio_bytes = await audio_file.read()

        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

        wav_file_in_memory = io.BytesIO()
        audio.export(wav_file_in_memory, format="wav")
        wav_file_in_memory.seek(0)

        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_file_in_memory) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")

            config = {"configurable": {"thread_id": thread_id}}

            resp = agent_executor.invoke({"messages": [HumanMessage(content=text)]}, config=config)
            result = resp['messages'][-2].artefact

            bot_answer = resp['messages'][-1].content

            return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Во время чтения файла произошла ошибка: {e}")