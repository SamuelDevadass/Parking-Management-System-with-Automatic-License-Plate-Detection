from fastapi import APIRouter, HTTPException
from services import detection

router = APIRouter()

@router.post("/api/detection/start")
def start_detection():
    detection.start_detection()
    return {"ok": True}


@router.get("/api/detection/status")
def detection_status():
    return detection.get_status()


@router.post("/api/detection/stop")
def stop_detection():
    detection.stop_detection()
    return {"ok": True}