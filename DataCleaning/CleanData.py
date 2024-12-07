import pandas as pd
import numpy as np
from DataCleaning.ExtractingFeatures import ExtractingFeatures
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
import requests
import json
import time
import matplotlib.pyplot as plt
import seaborn as sns

class CleanData:
    GEOCODE_API_KEY = "YOUR_GEOCODE_APi"
    MAPQUEST_API_KEY = "YOUR_MAPQUEST_API"
    def __init__(self, df: pd.DataFrame):
        self.df = df
            
    def preprocessing(self) -> None:
        """ Data is transformed to categorical and numerical types for imputations """
        imputing_data = pd.DataFrame()
        imputing_data["ID"] = [_ for _ in range(len(self.df))]
        imputing_data["Address"] = self.df["address"].apply(ExtractingFeatures.textExtract)
        imputing_data["Post Date"] = self.df["post_update"].apply(lambda lst: ExtractingFeatures.dateExtract(lst, component="Date")) 
        imputing_data["Quarter"] = self.df["post_update"].apply(lambda lst: ExtractingFeatures.dateExtract(lst, component="quarter"))
        # imputing_data["Day"] = self.df["post_update"].apply(lambda lst: ExtractingFeatures.dateExtract(lst, component="day"))
        # imputing_data["Month"] = self.df["post_update"].apply(lambda lst: ExtractingFeatures.dateExtract(lst, component="month"))
        imputing_data["Year"] = self.df["post_update"].apply(lambda lst: ExtractingFeatures.dateExtract(lst, component="year"))
        imputing_data["District"] = self.df["address"].apply(ExtractingFeatures.districtExtract)
        imputing_data["Price (billion VND)"] = self.df["price"].apply(ExtractingFeatures.priceExtract)
        imputing_data["Area (m2)"] = self.df["area"].apply(ExtractingFeatures.areaExtract)
        imputing_data["Property Type"] = self.df["property_type"].apply(ExtractingFeatures.typeExtract)
        imputing_data["Direction"] = self.df["direction"].apply(ExtractingFeatures.phraseExtract)
        imputing_data["Floors"] = self.df["floors"].apply(ExtractingFeatures.floorExtract)
        imputing_data["Bathrooms"] = self.df["bathrooms"].apply(ExtractingFeatures.roomsExtract)
        imputing_data["Entrance (m2)"] = self.df["entrance"].apply(ExtractingFeatures.entranceExtract)
        imputing_data["Bedrooms"] = self.df["bedrooms"].apply(ExtractingFeatures.roomsExtract)
        imputing_data["Living Rooms"] = self.df["livingrooms"].apply(ExtractingFeatures.roomsExtract)
        imputing_data["Law Document"] = self.df["law_doc"].apply(ExtractingFeatures.law_doc)
        imputing_data["Latitude"] = self.df["location"].apply(lambda lst: ExtractingFeatures.locationExtract(lst, component="latitude"))
        imputing_data["Longitude"] = self.df["location"].apply(lambda lst: ExtractingFeatures.locationExtract(lst, component="longitude"))
        imputing_data.dropna(subset=["Price (billion VND)"], inplace = True, ignore_index = True)
        self.df = imputing_data
        return 
    
    def nan_percentage(self) -> pd.Series:
        """ Returning the percentage of NaN values in each field AFTER The dataframe is processed """
        return round((self.df.isnull().sum()/len(self.df))*100, 2)
    
    def drop_field(self, series: pd.Series, cutoff: float) -> None:
        """ The DataFrame used here is preprocessed.
            Dropping fields with the percentage of NaN values exceeding a threshold set by the 'cutoff' parameter.
            series: the nan_percentage obtained from our dataframe
            cutoff: the percentage threshold """
        removed_fields = series[series >= cutoff].index
        self.df.drop(axis = 1, columns = removed_fields, inplace = True)
        return 
    
    def fill_predictors(self) -> None:
        """ After dropping all fields with a high percentage of NaN values from the preprocessed DataFrame, we want to excluded all properties that are not in Hanoi and create completed case data for our predictors in the imputation process. 
        In our case, the predictors are 'Quarter', 'Year', 'District', and 'Property Type'. Only 'District' requires further processing. 
        We also need to fill in missing values for the Latitude and Longitude columns based on the District field.
        """
        # Imputing missing District values by converting coordinates to addresses
        for i in range(len(self.df.index)):
            district = self.df.iloc[i]["District"]
            lat = self.df.iloc[i]["Latitude"]
            lng = self.df.iloc[i]["Longitude"]
            if pd.isna(district) and (not pd.isna(lat)) and (not pd.isna(lng)):
                url = f"https://geocode.maps.co/reverse?lat={lat}&lon={lng}&api_key={CleanData.GEOCODE_API_KEY}"
                response = requests.get(url)
                self.df.loc[i, "District"] = response.json()["address"].get("suburb")
                time.sleep(1)
            
        self.df.dropna(subset=["District"], inplace=True, ignore_index=True)
        
        # Removing data points that are not in Hanoi
        self.df["District"] = self.df["District"].apply(lambda x: x.lower().split("district")[0].strip()).apply(lambda txt: txt.replace('đ', 'd')).apply(ExtractingFeatures.remove_vietnamese_accents)
        for i in range(len(self.df.index)):
            if self.df["District"][i] in ["an phu ward", "go vap", "son tra", "phu nhuan", "hai chau", "bai chay", "cooksville", "binh thanh", "phuong son phong", "binh tan", "ha phong"] or self.df["District"][i] == '':
                self.df.loc[i, "District"] = np.NaN
            elif self.df["District"][i] in ["xa an khanh", "xa van canh"]:
                self.df.loc[i, "District"] = "hoai duc"
            elif self.df["District"][i] == "xa dang xa":
                self.df.loc[i, "District"] = "gia lam"
            elif self.df["District"][i] == "kim chung commune":
                self.df.loc[i, "District"] = "dong anh"
            elif self.df["District"][i] == "duc giang commune":
                self.df.loc[i, "District"] = "long bien"
        
        self.df.dropna(subset=["District"], inplace=True, ignore_index=True)
        
        # Imputing missing Latitude and Longitude values by converting addresses to coordinates
        for i in range(len(self.df)):
            if pd.isnull(self.df.at[i, "Latitude"]) or pd.isnull(self.df.at[i, "Longitude"]):
                parameters = {"key": CleanData.MAPQUEST_API_KEY, 
                      "location": self.df.at[i, "Address"]
                      }
                response = requests.get("https://www.mapquestapi.com/geocoding/v1/address", params= parameters)
                simplify = json.loads(response.text)["results"]
                latitude = simplify[0]["locations"][0]["latLng"]["lat"]
                longitude = simplify[0]["locations"][0]["latLng"]["lng"]
                self.df.loc[i, "Latitude"] = latitude
                self.df.loc[i, "Longitude"] = longitude
        return
    
    def numerical_convert(self, categorical_encoder) -> any:
        """ Return the converted DataFrame and the transformation dictionary """
        transform_dict = dict()
        converted_data = self.df.copy()
        object_cols = self.df.select_dtypes(include=["object"]).columns
        for col in object_cols:
            converted_data[col] = categorical_encoder.fit_transform(self.df[[col]])
            transform_dict[col] = list(zip(converted_data[col].unique(), self.df[col].unique()))
        self.df = converted_data
        return converted_data, transform_dict
    
    def correlation_map(self) -> None:
        """ Showing the correlation between any 2 variables """
        corr_matrix = self.df.corr()
        plt.figure(figsize=(10, 6))
        ax = sns.heatmap(corr_matrix, cmap="coolwarm", annot=True, fmt=".2f", linewidths=.5, linecolor="black")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        plt.title("Correlations between every 2 fields", fontweight="bold")
        return

    def VIF_values(self) -> pd.DataFrame:
        """ Showing the Variance Inflation Factor (VIF) for each field """
        X = add_constant(self.df)
        vif_df = pd.DataFrame()
        vif_df["Fields"] = X.columns
        vif_df["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
        return vif_df
