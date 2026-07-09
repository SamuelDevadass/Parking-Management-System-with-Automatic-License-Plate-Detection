-- Inferred from the queries in your original Tkinter app. You likely
-- already have this database — this file is just for reference, or for
-- spinning up a fresh dev database quickly.

CREATE TABLE IF NOT EXISTS has_wing_floor (
    wing TEXT NOT NULL,
    centre_id INTEGER NOT NULL,
    floor INTEGER
);

CREATE TABLE IF NOT EXISTS has_parking_spot (
    centre_id INTEGER NOT NULL,
    wing TEXT NOT NULL,
    floor INTEGER NOT NULL,
    spot_number INTEGER NOT NULL,
    size TEXT NOT NULL CHECK (size IN ('Two Wheeler', 'Four Wheeler')),
    availability BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (centre_id, wing, floor, spot_number)
);

CREATE TABLE IF NOT EXISTS owner (
    owner_id TEXT PRIMARY KEY,
    name TEXT
);

CREATE TABLE IF NOT EXISTS owner_phone (
    owner_id TEXT NOT NULL REFERENCES owner(owner_id),
    phone TEXT NOT NULL,
    PRIMARY KEY (owner_id, phone)
);

CREATE TABLE IF NOT EXISTS owns_vehicle (
    owner_id TEXT NOT NULL REFERENCES owner(owner_id),
    license_number TEXT PRIMARY KEY,
    model TEXT,
    colour TEXT,
    type TEXT CHECK (type IN ('Two Wheeler', 'Four Wheeler'))
);

CREATE TABLE IF NOT EXISTS parking_log (
    id SERIAL PRIMARY KEY,
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP,
    license_number TEXT NOT NULL,
    centre_id INTEGER NOT NULL,
    wing TEXT NOT NULL,
    floor INTEGER NOT NULL,
    spot_number INTEGER NOT NULL,
    image_folder_path TEXT,
    duration INTERVAL,
    amount NUMERIC
);
