import requests

VALID_LINES = {
    "bakerloo", "central", "circle", "district", "hammersmith & city",
    "jubilee", "metropolitan", "northern", "piccadilly", "victoria",
    "waterloo & city", "dlr", "london overground", "elizabeth line"
}

def find_zone(data):
    # Search recursively
    if isinstance(data, dict):
        # Direct 'zone' key
        if 'zone' in data:
            return data['zone']
        # Check additionalProperties
        if 'additionalProperties' in data:
            for prop in data['additionalProperties']:
                if prop.get('key', '').lower() == 'zone' and prop.get('value'):
                    # Handle multi-zone like "2+3"
                    return prop['value'].split('+')[0].strip()
        # Recurse through all dict values
        for value in data.values():
            result = find_zone(value)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_zone(item)
            if result is not None:
                return result
    return None

def get_station_info(station_id):
    """
    Fetch station info from TfL API.

    Returns:
        dict: Station name, number of platforms, lines, zones
    """
    try:
        url = f"https://api.tfl.gov.uk/StopPoint/{station_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Cleaned station name
        station_name = data.get("commonName", "").strip()
        if "Underground Station" in station_name:
            station_name = station_name.replace("Underground Station", "").strip()
        else:
            station_name = station_name.replace("Station", "").strip()
        
        # Platform counting (combo) 
        platform_ids = set()

        # Children
        for child in data.get("children", []):
            if child.get("stopType") == "NaptanMetroPlatform":
                naptan = child.get("naptanId") or child.get("id")
                if naptan:
                    platform_ids.add(naptan)

        # lineGroup
        for group in data.get("lineGroup", []):
            refs = group.get("naptanIdReference", [])
            if isinstance(refs, list):
                platform_ids.update(refs)
            elif isinstance(refs, str):
                platform_ids.add(refs)

        # Platform names from arrivals 
        platforms = set()
        try:
            arrivals_url = f"https://api.tfl.gov.uk/StopPoint/{station_id}/Arrivals"
            arr_resp = requests.get(arrivals_url, timeout=15)
            arr_resp.raise_for_status()
            arrivals = arr_resp.json()
            platforms = {a.get("platformName") for a in arrivals if a.get("platformName")}
        except Exception:
            platforms = set()

        # Combine both: if metadata is weak, arrivals helps
        num_platforms = len(platforms)

        # Extract lines
        # Lines (filter only valid TfL rail lines)
        lines = sorted({
            line["name"] for line in data.get("lines", [])
            if line.get("name") and line["name"].lower() in VALID_LINES
        })

        zone = find_zone(data)
        try:
            if zone is not None:
                zone = int(str(zone).split("+")[0].strip())  # handle '2+3' case
        except Exception:
            zone = None

        return {
            "station_name": station_name,
            "number_of_platforms": num_platforms,
            "lines": lines,
            "zones": zone
        }

    except Exception as e:
        return {"error": str(e)}

print(get_station_info("940GZZLUAGL"))