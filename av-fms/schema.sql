DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    vehicle_id INTEGER,
    -- vehicle_id is the id of the vehicle that the user took
    role TEXT CHECK(role IN ('STAFF', 'USER')) NOT NULL DEFAULT 'USER'
);
DROP TABLE IF EXISTS vehicle;
CREATE TABLE vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_plate_number TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    user_id INTEGER,
    -- user_id is this is the user who took the vehicle (if available == False)
    available BOOLEAN NOT NULL
);