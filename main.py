from Staton_info_scrapper import get_station_info
from station_ids import station_ids

def station_info_loop(station_ids):
    station_names = list(station_ids.keys())
    i = 30

    #while i < len(station_ids):
    while i < 38:   
        station = station_names[i]
        stop_ids = station_ids[station]

        seen_stations = {}        

        # Some stations may have multiple stop IDs
        for stop_id in stop_ids:
            info = get_station_info(stop_id)

            if "error" in info:
                print("="*10)
                print(f"Error fetching {station} ({stop_id}): {info['error']}")
                print("="*10)
                continue  # skip to next stop_id
            
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