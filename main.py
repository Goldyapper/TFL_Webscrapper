from Staton_info_scrapper import get_station_info
from station_ids import station_ids

def station_info_loop(station_ids):
    station_names = list(station_ids.keys())
    i = 0

    while i < 20:
        station = station_names[i]
        stop_ids = station_ids[station]

        # Some stations may have multiple stop IDs
        for stop_id in stop_ids:
            info = get_station_info(stop_id)

            if "error" in info:
                print("="*40)
                print(f"Error fetching {station} ({stop_id}): {info['error']}")
                print("="*40)
                continue  # skip to next stop_id

            print("="*40)
            print(f"Station: {info['station_name']}")
            print(f"Zone(s): {info['zones']}")
            print(f"Number of platforms: {info['number_of_platforms']}")
            print(f"Lines: {', '.join(info['lines'])}")
            print("="*40)

        i += 1

# Run the loop
station_info_loop(station_ids)