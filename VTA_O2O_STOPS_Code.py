import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

'''
I’ve implemented code to generate the O2O_STOPS sheet similarly to the original one.
Here's how it works:
I extracted the line name from the database (e.g., "BLUE_LINE_NB_ON" became "BlueLine").
From the details_file (sheet "STOPS"), I also extracted line names (e.g., "VTA_2_GreenLine_00" became "GreenLine").
I then compared the line names and stop names from both files.
If they matched, I included information such as ‘seq_fixed,’ ‘ETC_STOP_NAME,’ ‘ETC_STOP_ID,’ ‘ETC_ROUTE_ID,’ and ‘ETC_ROUTE_NAME’ from the database to build the final output.
'''

def check_all_code_columns(df, columns_to_check):
    # Function to clean a string by removing underscores and square brackets and converting to lowercase
    def clean_string(s):
        return s.replace('_', '').replace('[', '').replace(']', '').replace(' ','').replace('#','').lower()

    # Clean and convert all column names in df to lowercase for case-insensitive comparison
    df_columns_lower = [clean_string(column) for column in df.columns]

    # Clean and convert the columns_to_check list to lowercase for case-insensitive comparison
    columns_to_check_lower = [clean_string(column) for column in columns_to_check]

    # Use a list comprehension to filter columns
    matching_columns = [column for column in df_columns_lower if "code" in column]

    return matching_columns


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

def clean_string(s):
    return s.replace(':', '').replace('-', '').replace('_', '').replace('[', '').replace(']', '').replace(' ','').replace('#','').lower()


project_name='VTA'

df=pd.read_csv('vtaca2024rail_o2o_export_odbc.csv')

# df=df[df['INTERV_INIT']!='999']

detail_df=pd.read_excel('details_vta_CA_od_excel (1).xlsx',sheet_name='STOPS')

code_columns=check_all_code_columns(df,df.columns)

code_columns=check_all_characters_present(df,code_columns)
code_columns

detail_df['LineName']=detail_df['ETC_ROUTE_ID'].apply(lambda x: str(x).split('_')[2])

def get_line_name(row):
    if pd.notna(row['BLUE_LINE_NB_ON_Code_']) or pd.notna(row['BLUE_LINE_NB_OFF_Code_']):
        return 'BlueLine', row['BLUE_LINE_NB_ON']
    elif pd.notna(row['BLUE_LIME_SB_ON_Code_']) or pd.notna(row['BLUE_LIME_SB_OFF_Code_']):
        return 'BlueLine', row['BLUE_LIME_SB_ON']
    elif pd.notna(row['GREEN_LINE_NB_ON_Code_']) or pd.notna(row['GREEN_LINE_NB_OFF_Code_']):
        return 'GreenLine', row['GREEN_LINE_NB_ON']
    elif pd.notna(row['GREEN_LINE_SB_ON_Code_']) or pd.notna(row['GREEN_LINE_SB_OFF_Code_']):
        return 'GreenLine', row['GREEN_LINE_SB_ON']
    elif pd.notna(row['ORANGE_LINE_EB_ON_Code_']) or pd.notna(row['ORANGE_LINE_EB_OFF_Code_']):
        return 'OrangeLine', row['ORANGE_LINE_EB_ON']
    elif pd.notna(row['ORANGE_LINE_WB_ON_Code_']) or pd.notna(row['ORANGE_LINE_WB_OFF_Code_']):
        return 'OrangeLine', row['ORANGE_LINE_WB_ON']
    else:
        return 'Unknown', ''

df[['LineNameDatabase', 'STOP_NAME']] = df.apply(get_line_name, axis=1, result_type='expand')

unique_line_names=df['LineNameDatabase'].unique()
unique_line_names

unique_stop_names=df['STOP_NAME'].unique()
unique_stop_names

detail_df=detail_df.query('LineName.isin(@unique_line_names)')
detail_df.reset_index(inplace=True,drop=True)

results = []

# Loop through each combination of line name and stop name
for line_name in unique_line_names:
    for stop_name in unique_stop_names:
        # Filter the DataFrame based on the given conditions

        # filtered_df = detail_df.query(
        #     f'LineName == "{line_name}" and '
        #     f'ETC_STOP_NAME.str.lower().str.contains("{stop_name.lower()}") and '
        #     f'ETC_ROUTE_ID.str.split("_").str[-1] != "01"',
        #     engine='python'
        # )
        filtered_df = detail_df.query(
            f'LineName == "{line_name}" and '
            f'ETC_STOP_NAME.str.lower().str.contains("{stop_name.lower()}")',
            engine='python'
        )
        # If the combination is found, add the relevant data to the results
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                results.append({
                    'STOP_NAME': stop_name,
                    'STOP_ID': row['seq_fixed'],
                    'ETC_STOP_NAME': row['ETC_STOP_NAME'],
                    'note': '',  # Empty column for 'note'
                    'ETC_STOP_ID': row['ETC_STOP_ID'],
                    'ETC_ROUTE_ID': row['ETC_ROUTE_ID'],
                    'ETC_ROUTE_NAME': row['ETC_ROUTE_NAME']
                })


results_df = pd.DataFrame(results)
results_df.to_csv('O2O_STOPS_VTA_01.csv',index=False)