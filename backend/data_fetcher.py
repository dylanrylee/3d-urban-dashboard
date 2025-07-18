import requests

def fetch_calgary_data():
    """
    Fetch building data from NYC Open Data Building Footprints API (u9wf-3gbt).
    Returns a list of buildings with id, geometry, height, address, zoning, value, area, width, length.
    """
    url = "https://data.cityofnewyork.us/resource/u9wf-3gbt.geojson?$limit=100"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Optional: Fetch PLUTO for address, zoning, value
        pluto_url = "https://data.cityofnewyork.us/resource/64uk-42ks.json?$limit=100"
        pluto_response = requests.get(pluto_url)
        pluto_data = {item["bbl"]: item for item in pluto_response.json()} if pluto_response.status_code == 200 else {}
        buildings = []
        for idx, feature in enumerate(data.get("features", [])):
            bbl = feature.get("properties", {}).get("base_bbl", "Unknown")
            pluto_item = pluto_data.get(bbl, {})
            buildings.append({
                "id": idx,
                "geometry": feature.get("geometry", {"type": "Point", "coordinates": [0, 0]}),
                "height": float(feature.get("properties", {}).get("height_roof", 0.0)),
                "address": pluto_item.get("address", bbl),  # Fallback to BBL
                "zoning": pluto_item.get("zonedist1", "Residential"),  # Mock zoning
                "value": float(pluto_item.get("assessval", 500000.0)),  # Mock value
                "area": 500.0,  # Mock area (Point geometry can't calculate)
                "width": 20.0,  # Mock width
                "length": 25.0  # Mock length
            })
        return buildings
    except requests.RequestException as e:
        print(f"Error fetching NYC data: {e}")
        return [
            {
                "id": 0,
                "geometry": {"type": "Point", "coordinates": [-73.853456066604, 40.86366044155]},
                "height": 14.29,
                "address": "2044580014",
                "zoning": "R6",
                "value": 500000.0,
                "area": 500.0,
                "width": 20.0,
                "length": 25.0
            },
            {
                "id": 1,
                "geometry": {"type": "Point", "coordinates": [-74.135976948371, 40.635751973763]},
                "height": 8.64260519,
                "address": "5010820061",
                "zoning": "C4-4A",
                "value": 750000.0,
                "area": 600.0,
                "width": 25.0,
                "length": 24.0
            }
        ]