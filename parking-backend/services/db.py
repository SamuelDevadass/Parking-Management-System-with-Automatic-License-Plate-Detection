import os
from typing import Optional
import psycopg
from dotenv import load_dotenv
load_dotenv(".//.env")

CONNECTION_STRING = (
    f"dbname={os.getenv('DB_NAME')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PW')} "
    f"host={os.getenv('DB_HOST')}")


def get_connection():
    return psycopg.connect(CONNECTION_STRING)


# ---------------------------------------------------------------------------
# Wings
# ---------------------------------------------------------------------------
def list_wings() -> list[str]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT DISTINCT wing FROM has_wing_floor")
        return [row[0] for row in cur.fetchall()]

def get_centre_for_wing(wing: str) -> Optional[int]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT centre_id FROM has_wing_floor WHERE wing = %s", (wing,))
        result = cur.fetchone()
        return result[0] if result else None


# ---------------------------------------------------------------------------
# Spots
# ---------------------------------------------------------------------------
def get_spot_availability(wing: str) -> dict:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""SELECT COUNT(*) AS total_spots_two_wheeler,
                        COUNT(*) FILTER (WHERE availability = TRUE) AS free_spots_two_wheeler
                        FROM has_parking_spot WHERE wing = %s AND size = 'Two Wheeler'""",
                        (wing,),)
        total_spots_two_wheeler, free_spots_two_wheeler = cur.fetchone()

        cur.execute("""SELECT COUNT(*) AS total_spots_four_wheeler,
                    COUNT(*) FILTER (WHERE availability = True) AS free_spots_four_wheeler
                    FROM has_parking_spot WHERE wing = %s AND size = 'Four Wheeler'""",
                        (wing,),)
        total_spots_four_wheeler, free_spots_four_wheeler = cur.fetchone()

    return {"total_spots_two_wheeler": total_spots_two_wheeler, 
            "free_spots_two_wheeler": free_spots_two_wheeler,  
            "total_spots_four_wheeler": total_spots_four_wheeler, 
            "free_spots_four_wheeler": free_spots_four_wheeler,}

# ---------------------------------------------------------------------------
# Spots for entry 
# ---------------------------------------------------------------------------
def get_available_spots(wing: str, centre_id: int, size: str) -> list[dict]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT floor, spot_number, size
               FROM has_parking_spot
               WHERE centre_id = %s AND wing = %s AND size = %s AND availability = True
               ORDER BY floor, spot_number""",
            (centre_id, wing, size),
        )
        rows = cur.fetchall()
    return [{"floor": r[0], "spot_number": r[1], "size": r[2]} for r in rows]

# ---------------------------------------------------------------------------
# Vehicle / owner details  
# ---------------------------------------------------------------------------
def get_vehicle(license_plate: str) -> Optional[dict]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""SELECT owner_id, model, colour, type
                        FROM owns_vehicle WHERE license_number = %s""",
                        (license_plate,),)
        vehicle_row = cur.fetchone()
        if not vehicle_row:
            return None
        owner_id, model, colour, vehicle_type = vehicle_row

        cur.execute("SELECT phone FROM owner_phone WHERE owner_id = %s", (owner_id,))
        phone_row = cur.fetchone()

        cur.execute("SELECT name FROM owner WHERE owner_id = %s", (owner_id,))
        name_row = cur.fetchone()

    return {
        "owner_id": owner_id,
        "model": model,
        "colour": colour,
        "type": vehicle_type,
        "phone": phone_row[0] if phone_row else "",
        "name": name_row[0] if name_row else "",
    }


def save_vehicle( owner_id: str,license_plate: str,model: str,colour: str, 
                  vehicle_type: str, phone: str,name: str,) -> None:   
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO owner (owner_id, name) VALUES (%s, %s)
                        ON CONFLICT (owner_id) DO NOTHING""",
                        (owner_id, name),)
        
        cur.execute("""INSERT INTO owner_phone (owner_id, phone) VALUES (%s, %s)
                        ON CONFLICT (owner_id, phone) DO NOTHING""",
                        (owner_id, phone),)
        
        cur.execute("""INSERT INTO owns_vehicle (owner_id, license_number, model, colour, type)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (license_number) DO NOTHING""",
                        (owner_id, license_plate, model, colour, vehicle_type),)
        conn.commit()

# ---------------------------------------------------------------------------
# Entry  
# ---------------------------------------------------------------------------
def mark_entry(entry_time,
                license_plate: str, centre_id: int,
                wing: str, floor: int,
                spot_number: int, folder_path: str, ) -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO parking_log
                    (entry_time,license_number, centre_id, 
                     wing, floor, spot_number, image_folder_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (entry_time, license_plate, centre_id, wing, floor, spot_number, folder_path),)
        
        cur.execute("""UPDATE has_parking_spot SET availability = False
                        WHERE centre_id = %s AND wing = %s AND floor = %s AND spot_number = %s""",
                        (centre_id, wing, floor, spot_number),)
        conn.commit()


# ---------------------------------------------------------------------------
# Exit 
# ---------------------------------------------------------------------------
def get_active_session(license_plate: str) -> Optional[dict]:
    """The most recent parking_log row for this plate with no exit_time yet."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""SELECT entry_time, centre_id, wing, floor, spot_number
                        FROM parking_log WHERE license_number = %s 
                        AND exit_time IS NULL ORDER BY entry_time DESC LIMIT 1""",
                        (license_plate,),)
        row = cur.fetchone()
    if not row:
        return None
    return {
        "entry_time": row[0],
        "centre_id": row[1],
        "wing": row[2],
        "floor": row[3],
        "spot_number": row[4],
    }


def get_vehicle_type(license_plate: str) -> Optional[str]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""SELECT type FROM owns_vehicle 
                        WHERE license_number = %s""", (license_plate,))
        row = cur.fetchone()
        return row[0] if row else None


def record_exit(entry_time, exit_time,
                duration, amount: float,
                centre_id: int, wing: str,
                floor: int, spot_number: int, ) -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""UPDATE parking_log
                        SET exit_time = %s, duration = %s, amount = %s
                        WHERE entry_time = %s AND exit_time IS NULL""",
                        (exit_time, duration, amount, entry_time),)
        
        cur.execute("""UPDATE has_parking_spot SET availability = True
                        WHERE centre_id = %s AND wing = %s AND floor = %s AND spot_number = %s""",
                        (centre_id, wing, floor, spot_number),)
        conn.commit()


# ---------------------------------------------------------------------------
# Billing 
# ---------------------------------------------------------------------------
def get_latest_bill(license_plate: str) -> Optional[dict]:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""SELECT entry_time, exit_time, duration, amount
                        FROM parking_log WHERE license_number = %s AND exit_time IS NOT NULL
                        ORDER BY exit_time DESC LIMIT 1""",
                        (license_plate,),)
        row = cur.fetchone()
        if not row:
            return None
        entry_time, exit_time, duration, amount = row

        cur.execute("""SELECT o.name FROM owner o
                        JOIN owns_vehicle v ON v.owner_id = o.owner_id
                        WHERE v.license_number = %s""",
                        (license_plate,),)
        name_row = cur.fetchone()

    return {
        "entry_time": entry_time,
        "exit_time": exit_time,
        "duration": duration,
        "amount": amount,
        "owner_name": name_row[0] if name_row else None,
    }
