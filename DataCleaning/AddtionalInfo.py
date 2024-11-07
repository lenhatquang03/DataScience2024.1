import geopy
class AdditionalInfo():
    USER_AGENT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36"
    LOCATOR = geopy.Nominatim(user_agent= USER_AGENT)
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self.location = AdditionalInfo.LOCATOR.geocode(f"{self.latitude}, {self.longitude}").raw
  
    def extract_postal_code(self) -> int:
        postal_code = self.location.get("display_name").split(',')[-2].strip()
        if postal_code.isdigit():
            return int(postal_code)
        else:
            return 10000

    def extract_bounding_box(self) -> list:
        bounding_box = self.location.get("boundingbox")
        return bounding_box

    def extract_place_rank(self) -> int:
        rank = self.location.get("place_rank")
        return rank

    def extract_importance(self) -> float:
        importance = self.location.get("importance")
        return importance