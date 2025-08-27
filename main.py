from Staton_info_scrapper import get_station_info
from station_ids import station_ids

def station_info_loop(stations_dict):
    station_names = list(stations_dict.keys())
    i = 0

    while i < len(station_names):
        station = station_names[i]
        stop_ids = stations_dict[station]

        # Some stations may have multiple stop IDs
        for stop_id in stop_ids:
            info = get_station_info(stop_id)
            print("="*40)
            print(f"Station: {info['station_name']}")
            print(f"Zone(s): {info['zones']}")
            print(f"Number of platforms: {info['number_of_platforms']}")
            print(f"Lines: {', '.join(info['lines'])}")
            print("="*40)

        i += 1

# Run the loop
station_info_loop(station_ids)