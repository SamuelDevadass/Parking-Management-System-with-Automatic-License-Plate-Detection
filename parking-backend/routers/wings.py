from fastapi import APIRouter, HTTPException
from services import db

router = APIRouter()

@router.get("/api/wings")
def get_wings():
    return db.list_wings()

@router.get("/api/wings/{wing}/centre")
def get_centre(wing: str):
    centre_id = db.get_centre_for_wing(wing)
    if centre_id is None:
        raise HTTPException(status_code=404, detail=f"No centre found for wing '{wing}'")
    return {"centre_id": centre_id}
