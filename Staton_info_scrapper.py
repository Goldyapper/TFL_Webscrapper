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
def clean_line_name(name):
    name = name.strip()
    if name.lower() == "elizabeth line":
        return "Elizabeth"
    return name


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

def get_platform_from_wikipedia(station_name):
    """
    Extract number of platforms from a Wikipedia page.
    """
    soup = get_wikipedia_page(station_name)
    if not soup:
        return None

    rows = soup.select(".infobox tr")
    for row in rows:
        header = row.find("th")
        data = row.find("td")
        if header and data:
            if "number of platforms" in header.get_text(strip=True).lower():
                match = re.search(r'\d+', data.get_text(strip=True))
                if match:
                    return int(match.group(0))
    return None

def get_zone_from_wikipedia(station_name):
    """
    Extract fare zone(s) from a Wikipedia page.
    """
    soup = get_wikipedia_page(station_name)
    if not soup:
        return None

    rows = soup.select(".infobox tr")
    possible_headers = ["fare zone", "zone", "travelcard zone", "london fare zone"]

    for row in rows:
        header = row.find("th")
        data = row.find("td")
        if header and data:
            header_text = header.get_text(strip=True).lower()
            if any(h in header_text for h in possible_headers):
                zone_text = data.get_text(strip=True)
                # Remove parentheses and extra text
                zone_text = re.sub(r"\s*\(.*?\)", "", zone_text)
    return zone_text


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
        station_name = data.get("commonName", "").strip()
        station_name = station_name.replace("Underground Station", "").replace("Rail Station", "").replace("Station", "").strip()
        station_name = re.sub(r"\s*\(.*?\)", "", station_name).strip()
        

        wiki_station_name = station_name.replace(" ", "_")
        wiki_platforms = get_platform_from_wikipedia(wiki_station_name)
        
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
                zone = get_zone_from_wikipedia(station_name)
        else:
            zone = get_zone_from_wikipedia(station_name)

        return station_name,num_platforms,lines,zone
        

    except Exception as e:
        return {"error": str(e)}