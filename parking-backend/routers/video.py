from fastapi import APIRouter, HTTPException
from services import db

router = APIRouter()

@router.get("/api/video")
def video_feed():
    pass