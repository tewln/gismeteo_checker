CREATE TABLE IF NOT EXISTS weather (
    id SERIAL PRIMARY KEY,
    date DATE,
    temperature_morning INTEGER,
    temperature_evening INTEGER,
    pressure_morning INTEGER,
    pressure_evening INTEGER,
    cloudiness_morning VARCHAR(50),
    cloudiness_evening VARCHAR(50),
    precipitation_morning VARCHAR(50),
    precipitation_evening VARCHAR(50),
    wind_speed_morning INTEGER,
    wind_speed_evening INTEGER,
    wind_direction_morning VARCHAR(5),
    wind_direction_evening VARCHAR(5)
);