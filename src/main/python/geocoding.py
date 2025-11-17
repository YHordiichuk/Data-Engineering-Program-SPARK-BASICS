import requests

class GeocoderService:
    def __init__(self, api_key):
        self.api_key=api_key
        self.base_url='https://api.opencagedata.com/geocode/v1/json'

    def get_cord(self, address):
        params={
            "q": address,
            "key": self.api_key,
            "limit": 1
            }
        try:
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data=response.json()
            
            if data["results"]:
                geometry = data["results"][0]["geometry"]
                lat, lng = geometry["lat"], geometry["lng"]
                return lat, lng
            else:
                return None, None   
        except Exception as e:
            print(f"Error extracting data from geo api: {e}")
            return None, None