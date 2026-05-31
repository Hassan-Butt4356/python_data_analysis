import pandas as pd
import numpy as np
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

ke_df=pd.read_excel("COTA_KINGElvis.xlsx",sheet_name='Elvis_Review')
ke_df=ke_df[ke_df['INTERV_INIT']!=999]
ke_df=ke_df[ke_df['HAVE_5_MIN_FOR_SURVECode']==1]

df=pd.read_csv('elviscota2023obweekday_export_odbc.csv')

def check_all_characters_present(df, columns_to_check):
    # Function to clean a string by removing underscores and square brackets and converting to lowercase
    def clean_string(s):
        return s.replace('_', '').replace('[', '').replace(']', '').replace(' ','').replace('#','').lower()

    # Clean and convert all column names in df to lowercase for case-insensitive comparison
    df_columns_lower = [clean_string(column) for column in df.columns]

    # Clean and convert the columns_to_check list to lowercase for case-insensitive comparison
    columns_to_check_lower = [clean_string(column) for column in columns_to_check]

    # Use a list comprehension to filter columns
    matching_columns = [column for column in df.columns if clean_string(column) in columns_to_check_lower]

    return matching_columns

access_egres_walk_column_checks=['valaccesswalk','valegresswalk']
access_egres_walk_column=check_all_characters_present(df,access_egres_walk_column_checks)
access_egres_walk_column

ke_df=pd.merge(ke_df,df[['id',*access_egres_walk_column]],on='id',how='left',indicator=True)
ke_df['Matched'] = (ke_df['_merge'] == 'both').astype(int)
ke_df.drop(columns=['_merge','Matched'],inplace=True)

# condition where ['VAL_ACCESS_WALK', 'VAL_EGRESS_WALK'] ==1
condition1 = ke_df[access_egres_walk_column[0]] == 1
condition2 = ke_df[access_egres_walk_column[1]] == 1
access_egress_true = ke_df[condition1 & condition2]

access_egress_true.to_csv("FileName_Access_Egress_True.csv",index=False)

# condition where ['VAL_ACCESS_WALK', 'VAL_EGRESS_WALK'] !=1
condition1 = ke_df[access_egres_walk_column[0]] != 1
condition2 = ke_df[access_egres_walk_column[1]] != 1
access_egress_false = ke_df[condition1 | condition2]

access_egress_false.to_csv("FileName_Access_Egress_False.csv",index=False)
