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

# reference: Preprocessed dataset where only rows containing "Đang thương lượng" or np.NaN values are dropped.
reference = cleaner.df
# reference.to_csv("preprocessed.csv")

nan_percentage = cleaner.nan_percentage()
cleaner.drop_field(nan_percentage, cutoff=60)
cleaner.fill_predictors()
# cleaner.df.to_csv("UnImputedDataWithIDs.csv")

# Data imputations with the "mode" strategy
strategies = {"Bathrooms": "mode", 
              "Floors": "mode", 
              "Entrance (m2)": "mode", 
              "Bedrooms": "mode", 
              "Living Rooms": "mode", 
              "Area (m2)": "mode"}

preds_dict = {"Bathrooms": ["Quarter", "Year", "District", "Property Type", "Law Document"], 
             "Floors": ["Quarter", "Year", "District", "Property Type", "Law Document"],
             "Entrance (m2)": ["Quarter", "Year", "District", "Property Type", "Law Document"],
             "Bedrooms": ["Quarter", "Year", "District", "Property Type", "Law Document"],
             "Living Rooms": ["Quarter", "Year", "District", "Property Type", "Law Document"], 
             "Area (m2)": ["Quarter", "Year", "District", "Property Type", "Law Document"]}

si = SingleImputer(strategy = strategies, predictors= preds_dict)
imputed_data = si.fit_transform(cleaner.df)
# imputed_data.to_csv("ModeImputedDataWithIDs.csv")

# Including some features from the original preprocessed dataset
final = pd.merge(imputed_data, reference[["ID", "Post Date", "Address"]], how="inner", on="ID").drop("Unnamed: 0", axis=1)
# final.to_csv("DisplayedData.csv")