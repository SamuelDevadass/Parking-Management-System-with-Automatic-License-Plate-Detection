from fastapi import APIRouter, HTTPException
from datetime import datetime
from services import db
from schemas import EntryPayload, ExitPayload, VehiclePayload
from services.billing import calculate_bill_amount

router = APIRouter()

@router.get("/api/vehicles/{license_plate}")
def get_vehicle(license_plate: str):
    vehicle = db.get_vehicle(license_plate)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="""No details found for this license number. 
                                                        Please enter details manually""")
    return vehicle


@router.post("/api/vehicles")
def save_vehicle(payload: VehiclePayload):
    db.save_vehicle(owner_id=payload.owner_id,
                    license_plate=payload.license_plate,
                    model=payload.model,
                    colour=payload.colour,
                    vehicle_type=payload.type,
                    phone=payload.phone,
                    name=payload.name,)
    return {"ok": True}

@router.post("/api/entries")
def mark_entry(payload: EntryPayload):
    db.mark_entry(entry_time=datetime.now(),
                    license_plate=payload.license_plate, centre_id=payload.centre_id,
                    wing=payload.wing, floor=payload.floor,
                    spot_number=payload.spot_number, folder_path=payload.folder_path or "",)
    return {"ok": True}

@router.get("/api/vehicles/spot/{license_plate}")
def get_spot_details(license_plate: str):
    session = db.get_active_session(license_plate)
    if session:
        return { "spot_number" : session["spot_number"], "status" : True }
    else:
        return { "spot_number" : "", "status" : False }



@router.post("/api/exits")
def mark_exit(payload: ExitPayload):
    session = db.get_active_session(payload.license_plate)
    if session is None:
        raise HTTPException(status_code=404, 
                            detail="No active parking session found for this plate")

    vehicle_type = db.get_vehicle_type(payload.license_plate) 

    exit_time = datetime.now()
    entry_time = session["entry_time"]
    duration = exit_time - entry_time
    amount = calculate_bill_amount(duration.total_seconds(), vehicle_type)

    db.record_exit(entry_time=entry_time, exit_time=exit_time,
                    duration=duration, amount=amount,
                    centre_id=session["centre_id"], wing=session["wing"],
                    floor=session["floor"], spot_number=session["spot_number"],)

    return {
        "entry_time": entry_time.isoformat(),
        "exit_time": exit_time.isoformat(),
        "duration": str(duration),
        "amount": amount,
    }
