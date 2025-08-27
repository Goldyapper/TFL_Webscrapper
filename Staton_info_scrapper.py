import requests

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
        station_name = data.get("commonName", "").replace("Underground Station", "").strip()

        # --- Platform counting (combo) ---
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

        # --- Platform names from arrivals ---
        arrivals_url = f"https://api.tfl.gov.uk/StopPoint/{station_id}/Arrivals"
        try:
            arr_resp = requests.get(arrivals_url, timeout=15)
            arr_resp.raise_for_status()
            arrivals = arr_resp.json()
            arrival_platforms = {a.get("platformName") for a in arrivals if a.get("platformName")}
        except Exception:
            arrival_platforms = set()

        # Combine both: if metadata is weak, arrivals helps
        num_platforms = max(len(platform_ids), len(arrival_platforms))

        # Extract lines
        lines = [line["name"] for line in data.get("lines", [])]
        
        # Zone information
        zone = None
        if "zones" in data and data["zones"]:
            # take the first zone
            zone = int(data["zones"][0])
        else:
            for prop in data.get("additionalProperties", []):
                if prop.get("key") == "Zone":
                    # sometimes TfL gives comma-separated values (e.g., "2,3")
                    zone = int(prop.get("value").split(",")[0].strip())
                    break


        return {
            "station_name": station_name,
            "number_of_platforms": num_platforms,
            "lines": lines,
            "zones": zone
        }

    except Exception as e:
        return {"error": str(e)}

print(get_station_info("940GZZLUAGL"))