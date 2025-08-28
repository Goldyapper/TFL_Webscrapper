from Staton_info_scrapper import get_station_info
from station_ids import station_ids
import time

def fetch_with_retry(stop_id, station):
    wait = 1
    retries = 5
    for attempt in range(retries):
        info = get_station_info(stop_id)
        if "error" in info and "429" in info["error"]:
            print(f"Rate limit hit for {station}, retry {attempt+1} in {wait}s...")
            time.sleep(wait)
            wait *= 2  # exponential wait
        else:
            return info
    return {"error": f"Failed after {retries} retries for {stop_id}"}


def station_info_loop(station_ids):
    station_names = list(station_ids.keys())
    i = 0

    while i < len(station_ids):
    #while i < 38:   
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
            
            seen_stations[info["station_name"]] = info
        
        for info in seen_stations.values():
            print("="*10)
            print(f"Station: {info['station_name']}")
            print(f"Zone: {info['zones']}")
            print(f"Number of platforms: {info['number_of_platforms']}")
            print(f"Lines: {', '.join(info['lines'])}")
            print("="*10)

        i += 1

# Run the loop
station_info_loop(station_ids)