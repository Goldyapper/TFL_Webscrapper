import requests,wikipediaapi,re
from bs4 import BeautifulSoup

# Specify a wiki user
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='TFL_WebscraperBot/1.0 (adam.a.parsons15@gmail.com)'
)

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

def get_platform_from_wikipedia(station_name):
    """
    Fetch number of platforms from Wikipedia.
    Tries multiple common page suffixes and stops at first valid station page.
    """
    suffixes = ["_tube_station", "_railway_station", ""]
    headers = {
        "User-Agent": "TFL_WebscraperBot/1.0 (adam.a.parsons15@gmail.com)"
    }
    
    for suffix in suffixes:
        page_name = station_name.replace(" ", "_") + suffix
        page = wiki_wiki.page(page_name)
        
        if page.exists():
            #print(f"Found Wikipedia page: {page.fullurl}")
            url = page.fullurl
            try:
                resp = requests.get(url, timeout=15, headers=headers)
                resp.raise_for_status()
            except:
                continue
            
            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.select(".infobox tr")
            for row in rows:
                header = row.find("th")
                data = row.find("td")
                if header and data:
                    if "number of platforms" in header.get_text(strip=True).lower():
                        match = re.search(r'\d+', data.get_text(strip=True))
                        if match:
                            return int(match.group(0))
            # Page exists but no platform info found
            return None

    #print(f"No Wikipedia page found for {station_name}")
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

        # Platform counting (combo) 
        station_name = data.get("commonName", "").strip()
        # Cleaned station name
        if "Underground Station" in station_name:
            station_name = station_name.replace("Underground Station", "").strip()
        if "Rail" in station_name:
            station_name = station_name.replace("Rail", "").strip()
        else:
            station_name = station_name.replace("Station", "").strip()
        

        wiki_station_name = station_name.replace(" ", "_")
        wiki_platforms = get_platform_from_wikipedia(wiki_station_name)
        
        num_platforms = 0
        if wiki_platforms:
            num_platforms = wiki_platforms

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

#print(get_station_info("940GZZLUAGL"))