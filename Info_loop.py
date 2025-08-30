from Staton_info_scrapper import get_station_info
from Database_inserter import database_adder
import time

def fetch_with_retry(stop_id, station):
    wait = 1
    retries = 5
    for attempt in range(retries):
        info = get_station_info(stop_id)

        if isinstance(info, dict) and "error" in info:
            if "429" in info["error"]:
                print(f"Rate limit hit for {station}, retry {attempt+1} in {wait}s...")
                time.sleep(wait)
                wait *= 2  # exponential wait
            else:
                return info
        return info
    
    return {"error": f"Failed after {retries} retries for {stop_id}"}


def station_info_loop(station_ids):
    station_names = list(station_ids.keys())
    i = 0

    while i < len(station_ids):
        station = station_names[i]
        stop_ids = station_ids[station]

        seen_stations = {}        

        # Some stations may have multiple stop IDs
        for stop_id in stop_ids:
            info = fetch_with_retry(stop_id,station)

            if "error" in info:
                print("="*10)
                print(f"Error fetching {station} ({stop_id}): {info['error']}")
                print("="*10)
                continue  # skip to retry the id
            
            seen_stations[info[0]] = info
        
        for info in seen_stations.values():
            print("="*10)
            
            print(f"Station: {info[0]}")
            print(f"Number of platforms: {info[1]}")
            print(f"Lines: {', '.join(info[2])}")
            print(f"Zone: {info[3]}")
            database_adder(info)
            
            print("="*10)

        i += 1