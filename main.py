from autoimpute.imputations import SingleImputer
from DataCleaning.CleanData import CleanData
from DataCleaning.AddtionalInfo import AdditionalInfo
import pandas as pd

# READING THE DATA AND STACK THEM 
apartment = pd.read_json("CafeLand/data/hanoi_apartment.json")
private_house = pd.read_json("CafeLand/data/hanoi_private_house.json")
town_house = pd.read_json("CafeLand/data/hanoi_town_house.json")
villa = pd.read_json("CafeLand/data/hanoi_villa.json")
data = pd.concat([apartment, private_house, town_house, villa], ignore_index=True)

# START THE PRE-PROCESS FOR IMPUTATION
cleaner = CleanData(data)
cleaner.preprocessing()

# reference: Preprocessed dataset where only rows containing "Đang thương lượng" or np.NaN values are dropped.
reference = cleaner.df
# reference.to_csv("preprocessed.csv")

nan_percentage = cleaner.nan_percentage()
cleaner.drop_field(nan_percentage, cutoff=60)
cleaner.fill_predictors()
unimputed_data = cleaner.df
# unimputed.to_csv("UnImputedDataWithIDs.csv")

# DATA IMPUTATION WITH THE "MODE" STRATEGY
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

imputed_data = si.fit_transform(unimputed_data)
# imputed_data.to_csv("ModeImputedData.csv")

# ADDING MORE INFORMATION BASED ON THE CLEANED DATA
for i in range(len(imputed_data)):
    extractor = AdditionalInfo(imputed_data.at[i, "Latitude"], imputed_data.at[i, "Longitude"])
    imputed_data.loc[i, "Postal Code"] = extractor.extract_postal_code()
    imputed_data.loc[i, "Place Rank"] = extractor.extract_place_rank()
    imputed_data.loc[i, "Importance"] = extractor.extract_importance()
imputed_data.dropna(ignore_index=True, inplace=True)
# imputed_data.to_csv("final.csv")