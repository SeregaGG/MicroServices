import io
import random
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydub import AudioSegment
import speech_recognition as sr

router = APIRouter(prefix="/vacation_agent", tags=["Actions"])

@router.post("/start")
async def dialog_start():
    return { "message_id": random.choice((1, 2, 3)) }

@router.post("/voice_message_upload")
async def upload_audio_file(audio_file: UploadFile = File(...)):
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
            return {"transcribed_text": text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Во время чтения файла произошла ошибка: {e}")