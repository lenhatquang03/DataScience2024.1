import pandas as pd
from autoimpute.imputations import MultipleImputer, MiceImputer

class Imputer:
    def __init__(self, fields_to_impute, unimputed_df):
        ''' 
        fields_to_impute: A list of common fields across all preprocessed datasets used. 
        unimputed_df: The preprocessed dataset.'''
        self.fields_to_impute = fields_to_impute
        self.unimputed_df = unimputed_df
        self.data_to_impute = self.unimputed_df[fields_to_impute]
    
    def drop_minimal_variance(self) -> None:
        ''' 
        Fields having too little variance make it impossible to compute a positive definite covariance matrix, which is crucial in imputations.
        '''
        low_variance_fields = self.data_to_impute.var()[self.data_to_impute.var() < 1e-6].index
        # Updating self.fields_to_impute
        for field in low_variance_fields:
            self.fields_to_impute.remove(field)
        
        # Updating self.data_to_impute
        self.data_to_impute = self.unimputed_df[self.fields_to_impute]

    def high_corr_fields(self) -> list:
        ''' 
        Returning a list of highly correlated fields for PMM imputation process.
        '''
        selected_fields = []
        correlation_matrix = self.data_to_impute.corr()
        corr_pairs = correlation_matrix.abs().unstack().sort_values(ascending=False)
        # if field1, field2 are highly correlated and field2, field3 are highly correlated. Then selected_pairs = [field1, field2, field3] 
        for pair in corr_pairs.index:
            if 1 > corr_pairs[pair] > 0.95:
                field1, field2 = pair
                if len(selected_fields) == 0:
                    selected_fields.extend(pair)
                if field1 not in selected_fields and field2 in selected_fields:
                    selected_fields.append(field1)
                if field1 in selected_fields and field2 not in selected_fields:
                    selected_fields.append(field2)
        return selected_fields
    
    def weak_corr_fields(self) -> list:
        ''' 
        Returning a list of weakly correlated fields for imputations using MiceImputer. 
        '''
        highly_correlated_fields = self.high_corr_fields()
        # Taking the difference between fields_to_impute and highly_correlated_fields
        weak_corr_fields = list(set(self.fields_to_impute).difference(set(highly_correlated_fields)))

        # Adding an arbitrary fields from the highly_correlated_fields for imputation.
        weak_corr_fields.append(highly_correlated_fields[0])

        return weak_corr_fields
    
    def mice_imputer(self) -> None:
        ''' 
        Using MiceImputer to impute data between weakly correlated fields.
        '''
        imputer = MiceImputer()
        mice_imputed_fields = self.weak_corr_fields()
        mice_unimputed_data = self.data_to_impute[mice_imputed_fields]
        # transformed = [(1, 1st_imputed_dataset), (2, 2nd_imputed_dataset), ..., (5, 5th_imputed_dataset)]
        transformed = list(imputer.fit_transform(mice_unimputed_data))
        mice_imputed_datasets = [imputation[1] for imputation in transformed]

        # Combining several single imputed datasets to one dataset
        mice_aggregated_dataset = pd.DataFrame(sum(mice_imputed_datasets)/len(mice_imputed_datasets), columns = mice_imputed_fields)

        # Updating self.data_to_impute with fields imputed in aggregated dataset
        self.data_to_impute.loc[:, mice_imputed_fields] = mice_aggregated_dataset

    def pmm_imputer(self) -> None:
        ''' 
        Using PMM to impute the highly correlated fields based on the already imputed field (one that is in pmm_imputed_fields) by the MiceImputer
        '''
        pmm_imputed_fields = self.high_corr_fields()
        pmm_unimputed_data = self.data_to_impute[pmm_imputed_fields]
        
        # Setting the strategies (exclude the already full field)
        strategies = {key: value for (key, value) in [(field, "pmm") for field in pmm_imputed_fields[1:]]}
        mi = MultipleImputer(strategy= strategies)

        transformed = list(mi.fit_transform(pmm_unimputed_data))
        pmm_imputed_datasets = [imputation[1] for imputation in transformed]

        # Combining several single imputed datasets to one dataset
        pmm_aggregated_dataset = pd.DataFrame(sum(pmm_imputed_datasets)/len(pmm_imputed_datasets), columns = pmm_imputed_fields)

        # Updating self.data_to_impute with fields imputed in aggregated dataset
        self.data_to_impute.loc[:, pmm_imputed_fields] = pmm_aggregated_dataset
    
    def update_unimputed_data(self) -> None:
        '''
        Replacing the unimputed_data with the imputed data
        '''
        self.unimputed_df.loc[:, self.fields_to_impute] = self.data_to_impute
        for field in self.fields_to_impute:
            self.unimputed_df[field] = self.unimputed_df[field].round().astype(int)