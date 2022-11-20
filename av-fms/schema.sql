DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    vehicle_id INTEGER -- the id of the vehicle that the user took
);

DROP TABLE IF EXISTS vehicle;
CREATE TABLE vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_plate_number TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    user_id INTEGER, -- if available is false, this is the user who took the vehicle
    available BOOLEAN NOT NULL
);