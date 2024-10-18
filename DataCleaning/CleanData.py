import pandas as pd
from ExtractingFeatures import ExtractingFeatures
class CleanData:
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def preprocessing(self) -> pd.DataFrame:
        """ Data is temporarily processed for imputations. """
        imputing_data = pd.DataFrame()
        imputing_data["Day"] = self.df["post_update"].apply(lambda lst: ExtractingFeatures.dateExtract(lst, component="day"))
        imputing_data["Month"] = self.df["post_update"].apply(lambda lst: ExtractingFeatures.dateExtract(lst, component="month"))
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
        return imputing_data
    
    def nan_percentage(self) -> pd.Series:
        """ Returning the percentage of NaN values in each field AFTER The dataframe is processed """
        return round((self.df.isnull().sum()/len(self.df))*100, 2)
    
    def drop_field(self, series: pd.Series, cutoff: float) -> None:
        """ Dropping fields with the percentage of NaN values exceeding a threshold set by the 'cutoff' parameter.
            series: the nan_percentage obtained from our dataframe
            cutoff: the percentage threshold """
        removed_fields = series[series >= cutoff].index
        self.df.drop(axis = 1, columns = removed_fields, inplace = True)
        return 