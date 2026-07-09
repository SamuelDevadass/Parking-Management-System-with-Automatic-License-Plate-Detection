"""
Bill calculation — ported from Page2.calculate_bill_amount in the Tkinter
app. This used to run client-side; it moved here because a browser
shouldn't be trusted to compute what someone owes.

NOTE: I kept your original tiering logic as-is, but two of the conditions
are unreachable as written:
    elif 3 > total_hours < 4        # total_hours < 3 AND < 4 — but the
                                     # branch above already caught <= 3
Worth double-checking this pricing table matches what you actually intend
to charge before this goes anywhere near production. I didn't change the
behavior here, just moved it.
"""

import math


def calculate_bill_amount(total_seconds: float, vehicle_type: str) -> float:
    total_hours = math.ceil(total_seconds / 3600)
    base_amount = 40 if vehicle_type == "Four Wheeler" else 20

    if total_hours <= 3:
        extra_cost = 0
    elif 3 > total_hours < 4:
        extra_cost = 0.30 * (total_hours - 3)
    elif 4 <= total_hours < 5:
        extra_cost = 0.30 + (0.40 * (total_hours - 4))
    else:
        extra_cost = 0.30 + 0.40 + (0.50 * (total_hours - 5))

    return base_amount + extra_cost
