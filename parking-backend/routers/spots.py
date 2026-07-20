from fastapi import APIRouter, HTTPException
from services import db

router = APIRouter()

@router.get("/api/spots/availability")
def get_spot_availability(wing: str):
    return db.get_spot_availability(wing)


@router.get("/api/spots")
def get_available_spots(wing: str, centre_id: int, size: str):
    return db.get_available_spots(wing, centre_id, size)