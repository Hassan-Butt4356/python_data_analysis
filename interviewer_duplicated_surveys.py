import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


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

# df=pd.read_csv('elvisdenverco2024obweekday_export_odbc.csv')
df=pd.read_csv('elvisbartca2024interceptNEW_main_export_odbc(001).csv')
filename='details_project_od_BART.xlsx'

df['Completed']=pd.to_datetime(df['Completed'], errors='coerce')
df['Survey Date'] = df['Completed'].dt.date

df=df[(df['INTERV_INIT']!='999')]
df = df[(df['HAVE_5_MIN_FOR_SURVECode'] == 1)]

def details_dataframe(filename):
    details_df=pd.read_excel(filename,sheet_name='AIR')
    return details_df


home_airport_hotel_column_names=['originaddresslat','originaddresslong', 'destinaddresslat', 'destinaddresslong','originplacetype','homeaddresslat','homeaddresslong',
                                 'destinairportcode','destinplacetype']

def check_home_airport_hotel(df, details_df):

    # Loop through each row in the DataFrame 'df'

    data_list = check_all_characters_present(df,home_airport_hotel_column_names)
    data_list.sort()
    
    for _, row in df.iterrows():
        # Extract latitude and longitude values for origin and destination
        
        origin_addr_lat = row[data_list[6]]
        origin_addr_lng = row[data_list[7]]
        destin_addr_lat = row[data_list[0]]
        destin_addr_lng = row[data_list[1]]

        # Check if origin latitude and longitude are missing
        if pd.isna(origin_addr_lat) or pd.isna(origin_addr_lng):
            # Get the type of origin place
            origin_place_type = row['ORIGIN_PLACE_TYPE']
            lat_col, lng_col = None, None  # Initialize variables for latitude and longitude column names
            if not pd.isna(origin_place_type):
            # Determine the appropriate columns based on place type
                if 'hotel' in origin_place_type.lower() or 'home' in origin_place_type.lower():
                    lat_col, lng_col = 'HOME_ADDRESS_LAT','HOME_ADDRESS_LONG'
                elif 'airport' in origin_place_type.lower():
                    airport_destin_code = row['DESTIN_AIRPORTCode']
                    airport_row = details_df[details_df['LIME_CODE'] == airport_destin_code]
                    if not airport_row.empty:
                        lat_col, lng_col = 'lat6', 'lng6'

                # If valid latitude and longitude columns are found, populate the corresponding values
                if lat_col and lng_col:
                    df.at[row.name, 'ORIGIN_ADDRESS_LAT'] = row[lat_col]
                    df.at[row.name, 'ORIGIN_ADDRESS_LONG'] = row[lng_col]

        # Check if destination latitude and longitude are missing
        if pd.isna(destin_addr_lat) or pd.isna(destin_addr_lng):
            # Get the type of destination place
            destin_place_type = row['DESTIN_PLACE_TYPE']
            lat_col, lng_col = None, None  # Initialize variables for latitude and longitude column names
            if not pd.isna(destin_place_type):
#                 print("Destination place type is NaN, skipping this row")
#                 continue
            # Determine the appropriate columns based on place type
                if 'hotel' in destin_place_type.lower() or 'home' in destin_place_type.lower():
                    lat_col, lng_col = 'HOME_ADDRESS_LAT','HOME_ADDRESS_LONG'
                elif 'airport' in destin_place_type.lower():
                    airport_destin_code = row['DESTIN_AIRPORTCode']
                    airport_row = details_df[details_df['LIME_CODE'] == airport_destin_code]
                    if not airport_row.empty:
                        lat_col, lng_col = 'lat6', 'lng6'

                # If valid latitude and longitude columns are found, populate the corresponding values
                if lat_col and lng_col:
                    df.at[row.name, 'DESTIN_ADDRESS_LAT'] = row[lat_col]
                    df.at[row.name, 'DESTIN_ADDRESS_LONG'] = row[lng_col]
    # Return the DataFrame 'df' with the populated columns
    return df


origin_destin_columns_check=['originaddresslat','originaddresslong','destinaddresslat','destinaddresslong']
destin_columns_check=['destinaddresslat','destinaddresslong']
origin_columns_check=['originaddresslat','originaddresslong']
origin_destin_columns=check_all_characters_present(df,origin_destin_columns_check)
origin_columns=check_all_characters_present(df,origin_columns_check)
destin_columns=check_all_characters_present(df,destin_columns_check)

details_df=details_dataframe(filename)

df=check_home_airport_hotel(df,details_df)

duplicated_df = df[df.duplicated(subset=origin_destin_columns, keep=False)]

unique_intervs=df['INTERV_INIT'].unique()

final_duplicated_df = pd.DataFrame()
final_destin_duplicated_df = pd.DataFrame()
final_origin_duplicated_df = pd.DataFrame()
origin_data=[]
destin_data=[]
origin_destin_data=[]
for interv in unique_intervs:
    
    user_data = df[df['INTERV_INIT'] == interv]
    unique_dates = user_data['Survey Date'].unique()
    for date in unique_dates:
        
        date_data = user_data[user_data['Survey Date'] == date]

        # Check for duplicated rows based on origin, destination, and both combined
        user_origin_duplicated_df = date_data[date_data.duplicated(subset=origin_columns, keep=False)]
        user_destin_duplicated_df = date_data[date_data.duplicated(subset=destin_columns, keep=False)]
        user_duplicated_df = date_data[date_data.duplicated(subset=origin_destin_columns, keep=False)]
        
        total_records=date_data.shape[0]
        origin_flag_records=user_origin_duplicated_df.shape[0]
        origin_flag_records_ids=user_origin_duplicated_df['id'].values
        destin_flag_records=user_destin_duplicated_df.shape[0]
        destin_flag_records_ids=user_destin_duplicated_df['id'].values
        origin_destin_flag_records=user_duplicated_df.shape[0]
        origin_destin_flag_records_ids=user_duplicated_df['id'].values
        
        # Append results to the final DataFrames
        final_origin_duplicated_df = pd.concat([
            final_origin_duplicated_df, 
            user_origin_duplicated_df[['id', 'Survey Date', 'INTERV_INIT', 'ORIGIN_PLACE_TYPE', *origin_columns, 'HOME_ADDRESS_LAT', 'HOME_ADDRESS_LONG']]
        ])

        final_destin_duplicated_df = pd.concat([
            final_destin_duplicated_df, 
            user_destin_duplicated_df[['id', 'Survey Date', 'INTERV_INIT', *destin_columns, 'DESTIN_PLACE_TYPE', 'HOME_ADDRESS_LAT', 'HOME_ADDRESS_LONG']]
        ])

        final_duplicated_df = pd.concat([
            final_duplicated_df, 
            user_duplicated_df[['id', 'Survey Date', 'INTERV_INIT', 'ORIGIN_PLACE_TYPE', *origin_destin_columns, 'DESTIN_PLACE_TYPE', 'HOME_ADDRESS_LAT', 'HOME_ADDRESS_LONG']]
        ])
        origin_data.append({
            'INTERV INIT':interv,
            'Survey Date':date,
            'Origin Duplicated Records':origin_flag_records,
            'Total Records':total_records,
            'Origin Duplicated Percentage':round(origin_flag_records/total_records*100,2) if total_records > 0 else 0,
            "Origin Flags IDS":origin_flag_records_ids
            
        })
        destin_data.append({
            'INTERV INIT':interv,
            'Survey Date':date,
            'Origin Duplicated Records':destin_flag_records,
            'Total Records':total_records,
            'Origin Duplicated Percentage':round(destin_flag_records/total_records*100,2) if total_records > 0 else 0,
            "Origin Flags IDS":destin_flag_records_ids
            
        })
        origin_destin_data.append({
                'INTERV INIT':interv,
                'Survey Date':date,
                'Origin Destin Duplicated Records':origin_destin_flag_records,
                'Total Records':total_records,
                'Origin Destin Duplicated Percentage':round(origin_destin_flag_records/total_records*100,2) if total_records > 0 else 0,
                "Origin Destin Flags IDS":origin_destin_flag_records_ids

            })

# Reset index for all DataFrames after concatenation
final_origin_duplicated_df.reset_index(drop=True, inplace=True)
final_destin_duplicated_df.reset_index(drop=True, inplace=True)
final_duplicated_df.reset_index(drop=True, inplace=True)
origin_df=pd.DataFrame(origin_data)
destin_df=pd.DataFrame(destin_data)
origin_destin_df=pd.DataFrame(origin_destin_data)


with pd.ExcelWriter(f'INTERV_Duplicated_stats002.xlsx') as writer:
    origin_df.to_excel(writer, sheet_name="INTERV Daily Origin%", index=False)    
    destin_df.to_excel(writer, sheet_name="INTERV Daily Destin%", index=False)    
    origin_destin_df.to_excel(writer, sheet_name="INTERV Daily OriginDestin%", index=False)    
    final_origin_duplicated_df.to_excel(writer, sheet_name="INTERV Origin Duplicates", index=False)    
    final_destin_duplicated_df.to_excel(writer, sheet_name="INTERV Destin Duplicates", index=False)    
    final_duplicated_df.to_excel(writer, sheet_name="INTERV Overall Duplicates", index=False)

print('File Generated SuccessFully')