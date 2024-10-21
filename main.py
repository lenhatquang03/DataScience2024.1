from autoimpute.imputations import SingleImputer
from DataCleaning.CleanData import CleanData
import pandas as pd

# Reading the data and stack them 
apartment = pd.read_json("CafeLand/data/hanoi_apartment.json")
private_house = pd.read_json("CafeLand/data/hanoi_private_house.json")
town_house = pd.read_json("CafeLand/data/hanoi_town_house.json")
villa = pd.read_json("CafeLand/data/hanoi_villa.json")
data = pd.concat([apartment, private_house, town_house, villa], ignore_index=True)

# Start the preprocess for imputations
cleaner = CleanData(data)
cleaner.preprocessing()
nan_percentage = cleaner.nan_percentage()
cleaner.drop_field(nan_percentage, cutoff=60)
cleaner.fill_predictors()

# Data imputations with the "mode" strategy
strategies = {"Bathrooms": "mode", 
              "Floors": "mode", 
              "Entrance (m2)": "mode", 
              "Bedrooms": "mode", 
              "Living Rooms": "mode", 
              "Area (m2)": "mode"}

preds_dict = {"Bathrooms": ["Quarter", "Year", "District", "Price (billion VND)", "Property Type", "Law Document"], 
             "Floors": ["Quarter", "Year", "District", "Price (billion VND)", "Property Type", "Law Document"],
             "Entrance (m2)": ["Quarter", "Year", "District", "Price (billion VND)", "Property Type", "Law Document"],
             "Bedrooms": ["Quarter", "Year", "District", "Price (billion VND)", "Property Type", "Law Document"],
             "Living Rooms": ["Quarter", "Year", "District", "Price (billion VND)", "Property Type", "Law Document"], 
             "Area (m2)": ["Quarter", "Year", "District", "Price (billion VND)", "Property Type", "Law Document"]}

si = SingleImputer(strategy = {"Bathrooms": "pmm", 
                                 "Floors": "pmm", 
                                 "Entrance (m2)": "pmm", 
                                 "Bedrooms": "pmm", 
                                 "Living Rooms": "pmm", 
                                 "Area (m2)": "pmm"}, predictors= preds_dict, return_list=True)

imputed_data = si.fit_transform(data)
imputed_data.to_csv("ModeImputedData.csv")