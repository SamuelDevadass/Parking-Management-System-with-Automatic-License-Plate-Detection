"""
Pydantic models for request bodies. FastAPI uses these to validate incoming
JSON and to auto-generate the /docs page — this is the main thing you don't
get for free with plain Flask, and it's why a mismatched field name from the
frontend shows up as a clear 422 error instead of a silent bug.
"""

from pydantic import BaseModel
from typing import Optional


class VehiclePayload(BaseModel):
    owner_id: str
    license_plate: str
    model: str
    colour: str
    type: str
    phone: str
    name: str


class EntryPayload(BaseModel):
    license_plate: str
    centre_id: int
    wing: str
    floor: str
    spot_number: str
    folder_path: Optional[str] = ""


class ExitPayload(BaseModel):
    license_plate: str
