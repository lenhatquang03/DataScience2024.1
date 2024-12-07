class OutliersRemoval:
    '''
    Used at the final stage, where all datasets have been cleaned, imputed, and combined into a finalized_df.
    '''
    def __init__(self, finalized_df):
        self.df = finalized_df

    def remove_outliers(self, column, threshold = 1.5) -> None:
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR

        self.df = self.df[(self.df[column] >= lower_bound) & (self.df[column] <= upper_bound)]