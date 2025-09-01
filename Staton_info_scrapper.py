import requests,wikipediaapi,re
from bs4 import BeautifulSoup

API_KEY =  "f541056479e94b49bd2f18167e45ea6b"

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

HARDCODED_PLATFORMS = {
    "Edgware Road": 6,
    "Hammersmith": 7, 
    "Heathrow Airport Terminal 4": 3,
    "Heathrow Airport Terminal 5": 6,
    "Kensington": 3, 
    "King's Cross & St Pancras International": 8,
    "Paddington": 8,
    "Liverpool Street": 10,
    "Reading": 4,
    "Stratford" : 10,
    "London Bridge": 4,
    "Maidenhead": 2,
    "Slough": 2,
    "Twyford": 2,
    "Finsbury Park": 4,
    "Moorgate": 8
}

def clean_line_name(name):
    name = name.strip()
    if name.lower() == "elizabeth line":
        return "Elizabeth"
    return name

def find_zone(data):
    if isinstance(data, dict):
        if 'zone' in data:
            return clean_zone(data['zone'])
        if 'additionalProperties' in data:
            for prop in data['additionalProperties']:
                if prop.get('key', '').lower() == 'zone' and prop.get('value'):
                    return clean_zone(prop['value'])
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

def clean_zone(zone_str):
    """Normalize TfL zone strings into the lowest number (int)."""
    if not zone_str:
        return None

    # Replace 'and', '/', etc. with '+'
    zone_str = re.sub(r'\s*(and|/)\s*', '+', zone_str.lower())

    # Extract digits
    parts = re.findall(r"\d+", zone_str)
    if not parts:
        return None

    # Return the lowest zone as int
    return int(min(parts, key=int))


def get_wikipedia_page(station_name):
    """
    Try common Wikipedia page suffixes and return BeautifulSoup object if found.
    """
    suffixes = ["_tube_station", "_railway_station", ""]

    for suffix in suffixes:
        page_name = station_name.replace(" ", "_") + suffix
        page = wiki_wiki.page(page_name)

        if page.exists():
            url = page.fullurl
            try:
                resp = requests.get(url, timeout=15, headers={
                    "User-Agent": "TFL_WebscraperBot/1.0 (adam.a.parsons15@gmail.com)"
                })
                resp.raise_for_status()
            except:
                continue

            return BeautifulSoup(resp.text, "html.parser")
    return None

def normalize_station_name(name: str) -> str:
    """
    Clean station names so they match hardcoded overrides.
    """
    # Remove things in parentheses
    name = re.sub(r"\s*\(.*?\)", "", name)
    # Standardize common Heathrow variations
    name = name.replace("Heathrow Terminal", "Heathrow Airport Terminal")
    return name.strip()

def get_platform_from_wikipedia(station_name):
    clean_name = normalize_station_name(station_name)

    if clean_name in HARDCODED_PLATFORMS:
        return HARDCODED_PLATFORMS[clean_name]

    soup = get_wikipedia_page(station_name)
    if not soup:
        return None

    rows = soup.select(".infobox tr")
    possible_headers = ["number of platforms", "platforms"]  # expanded list

    for row in rows:
        header = row.find("th")
        data = row.find("td")
        if header and data:
            header_text = header.get_text(strip=True).lower()
            if any(h in header_text for h in possible_headers):
                match = re.search(r'\d+', data.get_text(strip=True))
                if match:
                    return int(match.group(0))

    return None

def get_station_info(station_id):
    """
    Fetch station info from TfL API.

    Returns:
        dict: Station name, number of platforms, lines, zones
    """
    try:
        url = f"https://api.tfl.gov.uk/StopPoint/{station_id}"
        params = {"app_key": API_KEY}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Platform counting (combo) 
        station_name = data.get("commonName", "").strip()
        # Cleaned station name
        station_name = data.get("commonName", "").strip()
        station_name = station_name.replace("Underground Station", "").replace("Rail Station", "").replace("Station", "").strip()
        station_name = re.sub(r"\s*\(.*?\)", "", station_name).strip()
        

        wiki_station_name = station_name.replace(" ", "_")
        wiki_platforms = get_platform_from_wikipedia(station_name)
        
        num_platforms = 0
        if wiki_platforms:
            num_platforms = wiki_platforms

        # Extract lines
        # Lines (filter only valid TfL rail lines)
        lines = sorted({
            clean_line_name(line["name"])
            for line in data.get("lines", [])
            if line.get("name") and line["name"].lower() in VALID_LINES
        })

        zone = find_zone(data)
        if zone is not None:
            try:
                zone = int(str(zone).split("+")[0].strip())
            except Exception:
                zone = clean_zone(find_zone(station_name))
        else:
            zone = clean_zone(find_zone(station_name))

        # Fallback for NR stations outside London
        if zone is None:
            zone = 6
        return station_name,num_platforms,lines,zone
        

    except Exception as e:
        return {"error": str(e)}

#print(get_station_info("940GZZLUBBB"))