import pandas as pd
import numpy as np

from datetime import date

import os
import warnings

warnings.filterwarnings("ignore")

today_date = date.today()
today_date=''.join(str(today_date).split('-'))

project_name='BUFFALO'

ke_df=pd.read_excel("Buffalo_NY_OB_KINGElvis.xlsx",sheet_name='Elvis_Review')
df=pd.read_csv('elvisbuffalony2024obweekday_export_odbc.csv')

ke_df=ke_df[ke_df['INTERV_INIT']!=999]
ke_df=ke_df[ke_df['HAVE_5_MIN_FOR_SURVECode']==1]



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

origin_destin_transport_column_checks=['origintransport','origintransportother','destintransport','destintransportother']
origin_destin_transport_column=check_all_characters_present(df,origin_destin_transport_column_checks)
origin_destin_transport_column

ke_df=pd.merge(ke_df,df[['id',*origin_destin_transport_column]],on='id',how='left',indicator=True)
ke_df['Matched'] = (ke_df['_merge'] == 'both').astype(int)
ke_df.drop(columns=['_merge'],inplace=True)

filtered_df = ke_df.query(
    "ORIGIN_TRANSPORT_y.str.contains(r'\\bOther\\b', case=False) or DESTIN_TRANSPORT_y.str.contains(r'\\bOther\\b', case=False)", 
    engine='python'
)




filtered_df.to_csv(f'reviewtool_{today_date}_{project_name}_OD_Transport_Mode_Checks.csv',index=False)

print('File Generated SuccessFully')