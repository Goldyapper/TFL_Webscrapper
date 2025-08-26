import requests

def get_station_info(station_id="940GZZLUACT"):
    """
    Fetch station info from TfL API.

    Returns:
        dict: Station name, number of platforms, platforms, lines
    """
    try:
        url = f"https://api.tfl.gov.uk/StopPoint/{station_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Cleaned station name
        station_name = data.get("commonName", "").replace("Underground Station", "").strip()

        # Extract platforms
        num_platforms = sum(
            1
            for child in data.get("children", [])
            if child.get("stopType") == "NaptanMetroPlatform"
        )


        # Extract lines
        lines = [line["name"] for line in data.get("lines", [])]

        # Zone information
        zones = ""
        # Option 1: TfL often has "zones" list directly
        if "zones" in data:
            zones = data["zones"]
        else:
            # Option 2: check additionalProperties
            for prop in data.get("additionalProperties", []):
                if prop.get("key") == "Zone":
                    zones = [int(z.strip()) for z in prop.get("value", "").split(",")]
                    break

        return {
            "station_name": station_name,
            "number_of_platforms": num_platforms,
            "lines": lines,
            "zones": zones
        }

    except Exception as e:
        return {"error": str(e)}

print(get_station_info())