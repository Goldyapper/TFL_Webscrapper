import sqlite3
from Staton_info_scrapper import get_station_info

def database_adder(station_info):
    
    station_name = station_info[0] if station_info[0] else None
    platforms = station_info[1] if station_info[1] else None
    lines = ', '.join(station_info[2]) if station_info[2] else None
    zone = station_info[3] if station_info[3] else None

    
    # Connect to SQLite DB
    conn = sqlite3.connect('tube.db')
    cursor = conn.cursor()

    # Create table 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stations (
        id INTEGER PRIMARY KEY,
        station_name TEXT NOT NULL,
        platforms INTEGER,
        lines TEXT,
        zone INTEGER
    )
    ''')

    # Get the highest ID manually
    cursor.execute('SELECT MAX(id) FROM stations')
    result = cursor.fetchone()
    id = (result[0] or 0) + 1


    cursor.execute('''
    INSERT INTO Stations (id, station_name, platforms, lines, zone)
    VALUES (?, ?, ?, ?, ?)
    ''', (id, station_name, platforms, lines, zone))

    print((id, station_name, platforms, lines, zone))


    # Save and close
    conn.commit()
    print("success")
    conn.close()

database_adder(get_station_info("940GZZLUHCL"))
database_adder(get_station_info("910GBONDST"))