# Gatehouse — FastAPI Backend

Ported from your Tkinter app: `db.py` is basically every `psycopg` call you
had scattered across `Select_Wing_Page`, `Page1`, `Page2`, `Page3`, pulled
into one place; `main.py` exposes each one as a route.

## Setup

```bash
cd parking-backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

cp .env.example .env            # then fill in your real DB credentials
pip install -r requirements.txt # the detection deps (yolo/ocr) are heavy —
                                 # comment them out in requirements.txt if
                                 # you just want the DB routes working first

uvicorn main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** — FastAPI auto-generates an interactive
page where you can call each route by hand and see the exact JSON it
returns, before the React frontend ever touches it. Genuinely the fastest
way to debug a mismatch between what the frontend expects and what the
backend sends.

`schema.sql` has the table definitions I inferred from your original SQL,
in case you're setting up a fresh database rather than reusing an existing
one.

## File map (→ where it came from in your Tkinter app)

| File | Tkinter equivalent |
|---|---|
| `db.py` | every inline `psycopg.connect(...)` block, across all pages |
| `main.py` | the routes that call `db.py` — no SQL lives here directly |
| `billing.py` | `Page2.calculate_bill_amount` |
| `detection.py` | `Detection_Page`'s thread + `queue.Queue` + `self.after(100, poll)` |
| `LicensePlateDetector.py` | unchanged — your detection pipeline |
| `schemas.py` | new — request validation FastAPI needs that Tkinter didn't |

## Two things that moved, worth knowing about

1. **Bill calculation moved from the frontend to `billing.py`.** In the
   Tkinter version this math lived in the GUI (`Page2`). A browser
   shouldn't be trusted to compute a price — it now happens here, and the
   frontend just displays whatever this returns. I preserved your original
   tiering logic exactly (see the comment in `billing.py` — two of the
   branches are actually unreachable as originally written, worth a look).

2. **Detection is now polled instead of pushed.** Your Tkinter thread wrote
   results into a `queue.Queue` that the GUI thread checked every 100ms.
   Over HTTP there's no shared memory to hand a queue through, so
   `detection.py` keeps the same result in a plain dict, and the frontend
   polls `GET /api/detection/status` once a second instead — same pattern,
   HTTP instead of in-process.

## Testing a route without the frontend

```bash
curl http://localhost:8000/api/wings
curl "http://localhost:8000/api/spots/availability?wing=A"
```

If a route 404s or the JSON shape looks wrong, check it directly against
the contract comment at the top of `src/api/client.js` in the frontend
project — that comment block is the source of truth both sides were built
against.
