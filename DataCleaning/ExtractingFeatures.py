import numpy as np
import regex as re
import math
import unicodedata
import pandas as pd
from datetime import datetime

class ExtractingFeatures:
    DISTRICTS = ["ba đình", "cầu giấy", "hoàn kiếm", "hai bà trưng", "hoàng mai", "đống đa", "tây hồ", "thanh xuân", "hà đông", "long biên", "ba vì", "chương mỹ", "đan phượng", "đông anh", "gia lâm", "hoài đức", "mê linh", "mỹ đức", "phú xuyên", "phúc thọ", "quốc oai", "sóc sơn", "thạch thất", "thanh oai", "thanh trì", "thường tín", "ứng hòa", "sơn tây"]
    
    @staticmethod
    def remove_vietnamese_accents(text) -> any:
        if pd.isna(text):
            return
        text = unicodedata.normalize("NFD", text)
        text = ''.join(char for char in text if unicodedata.category(char) != "Mn")
        return unicodedata.normalize("NFC", text)
    
    @staticmethod
    def phraseExtract(lst: list) -> str:
        """ Extract phrases in a single line """
        if len(lst) == 0:
            return np.NaN
        return ExtractingFeatures.remove_vietnamese_accents(lst[0].strip())
    
    @staticmethod
    def textExtract(lst: list) -> str:
        if len(lst) == 0:
            return np.NaN
        rawText = list(map(str.strip, lst))
        return ExtractingFeatures.remove_vietnamese_accents(''.join(txt for txt in rawText))
    
    @staticmethod
    def law_doc(lst: list) -> str:
        """ Check if the property has already had an attached law document ot not """
        if len(lst) == 0:
            return "Not provided"
        else:
            document = ExtractingFeatures.phraseExtract(lst)
            if document in ["So hong", "Hop đong", "Giay đo", "Giay to hop le", "Giay tay", "Chu quyen tu nhan"]:
                return "Yes"
            elif document == "Đang hop thuc hoa":
                return "In Progress"
            elif document == "Khong xac đinh":
                return "Not Provided"
        
    @staticmethod
    def districtExtract(lst: list) -> str:
        """ Extracting the district the house is in """
        if len(lst) == 0:
            return np.NaN
        
        for text in lst:
            if "hà nội" in text.lower():
                raw_address = text.lower().strip()
                break

        for district in ExtractingFeatures.DISTRICTS:
            if district in raw_address:
                return ExtractingFeatures.remove_vietnamese_accents(district)
        return np.NaN
    
    @staticmethod
    def typeExtract(lst: list) -> str:
        if len(lst) == 0:
            return np.NaN
        
        rawType = lst[0].strip()
        return ExtractingFeatures.remove_vietnamese_accents(rawType.split("Bán ")[1])

    @staticmethod
    def dateExtract(lst: list, component: str) -> any:
        """ Return the date in form of Python datetime object """
        if len(lst) == 0:
            return np.NaN
        
        rawDate = lst[0].split(": ")[-1]
        day_month_year = rawDate.split('-')
        if component == "day":
            return int(day_month_year[0])
        elif component == "month":
            return int(day_month_year[1])
        elif component == "year":
            return int(day_month_year[-1])
        elif component == "quarter":
            return math.ceil(int(day_month_year[1])/3)
        else:
            return datetime(int(day_month_year[-1]), int(day_month_year[1]), int(day_month_year[0]))
    
    @staticmethod
    def priceExtract(lst: list) -> float:
        """ Returning the property's price in billion VND."""
        if len(lst) == 0:
            return np.NaN
        
        rawPrice = lst[0]
        num_extract = re.findall("\d{1,5}", rawPrice)
        if ("tỷ" in rawPrice) and ("triệu" in rawPrice):
            return float(f"{num_extract[0]}.{num_extract[1]}")
        elif ("tỷ" in rawPrice) and ("triệu" not in rawPrice):
            return float(f"{num_extract[0]}")
        elif ("tỷ" not in rawPrice) and ("triệu" in rawPrice):
            return float(f"0.{num_extract[0]}")    
        else:
            return np.NaN
        
    @staticmethod
    def areaExtract(lst: list) -> float:
        """ Returning the property's area in m2 """
        if len(lst) == 0:
            return np.NaN
        
        rawArea = lst[0]
        if "PN" in rawArea:
            return np.NaN
        else:
            area = float(rawArea.split("m2")[0].replace(',', '.'))
            return area
        
    @staticmethod
    def floorExtract(lst: list) -> int:
        if len(lst) == 0:
            return np.NaN
    
        rawFloor = lst[0].strip()
        if rawFloor.isdigit():
            return int(rawFloor)
        else:
            return int(rawFloor.split(" ")[0])
        
    @staticmethod
    def roomsExtract(lst: list) -> int:
        """ Extracting the number of rooms of different types (bathroom, bedroom, and living room)"""
        if len(lst) == 0:
            return np.NAN
    
        rawRooms = lst[0].strip()
        return int(rawRooms.split(" ")[0])
    
    @staticmethod
    def entranceExtract(lst: list) -> float:
        """ Extracting the property's entrance width in metres (m). """
        if len(lst) == 0:
            return np.NaN
        rawEntrance = list(map(float, re.findall("\d{1,3}", lst[0])))
        return float(sum(rawEntrance)/len(rawEntrance))
        
    @staticmethod
    def locationExtract(lst: list, component: str) -> any:
        """ Extracting the (latitude, longitude) pair of a property's location """
        if len(lst) == 0:
            return np.NaN
    
        rawLocation = lst[0]
        rawCoordinate = re.search(r"q=(.*?)&hl=es", rawLocation).group(1)
        rawLatitude = rawCoordinate.split(',')[0]
        rawLongitude = rawCoordinate.split(',')[1]
        if rawLatitude == "" or rawLongitude == "":
            return np.NaN
        else:
            if component == "latitude":
                return float(rawLatitude)
            elif component == "longitude":
                return float(rawLongitude)
            else: 
                return (float(rawCoordinate.split(',')[0]), float(rawCoordinate.split(',')[1]))