import uuid
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.schemas import HealthResponse, TuningResult
from app.detectors.pitch_detector import PitchDetector
from app.detectors.note_finder import NoteFinder
from app.websocket.manager import ConnectionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = PitchDetector(sample_rate=settings.SAMPLE_RATE)
note_finder = NoteFinder()
manager = ConnectionManager()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка работоспособности"""
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME
    )

@app.websocket("/ws/tuner")
async def websocket_tuner(websocket: WebSocket):
    """
    WebSocket для тюнера
    
    Клиент отправляет: аудиоданные (bytes, Float32)
    Сервер отвечает: { "frequency": 440.0, "note": "A4", "cents": 0, ... }
    """
    client_id = str(uuid.uuid4())[:8]
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            audio_data = await websocket.receive_bytes()
            
            frequency, is_silence = detector.detect(audio_data)
            
            if is_silence or frequency == 0:
                await manager.send_message(client_id, {
                    "type": "tuning",
                    "frequency": 0,
                    "note": None,
                    "cents": 0,
                    "is_in_tune": False,
                    "suggestion": "play"
                })
                continue
            
            note, cents = note_finder.frequency_to_note(frequency)
            
            string = note_finder.get_guitar_string(frequency)
            
            is_in_tune = abs(cents) < 5 if note else False
            
            if note:
                if cents < -10:
                    suggestion = "down"
                elif cents > 10:
                    suggestion = "up"
                elif abs(cents) <= 5:
                    suggestion = "good"
                else:
                    suggestion = "a bit off"
            else:
                suggestion = "louder"
            
            result = {
                "type": "tuning",
                "frequency": round(frequency, 1),
                "note": note,
                "cents": cents,
                "string": string,
                "is_in_tune": is_in_tune,
                "suggestion": suggestion
            }
            
            await manager.send_message(client_id, result)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Error in websocket: {e}")
        manager.disconnect(client_id)