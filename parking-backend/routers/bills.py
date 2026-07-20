from fastapi import APIRouter, HTTPException
from services import db
router = APIRouter()


@router.get("/api/bills/{license_plate}/latest")
def get_latest_bill(license_plate: str):
    bill = db.get_latest_bill(license_plate)
    if bill is None:
        raise HTTPException(status_code=404, detail="No completed session found for this plate")
    return {
        "entry_time": bill["entry_time"].strftime("%Y-%m-%d %H:%M:%S"),
        "exit_time": bill["exit_time"].strftime("%Y-%m-%d %H:%M:%S"),
        "duration": str(bill["duration"]),
        "amount": bill["amount"],
        "owner_name": bill["owner_name"],
    }