import pandas as pd
import numpy as np
from datetime import date,datetime
from rapidfuzz import process, fuzz
from geopy.distance import geodesic
import warnings
import copy

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

today_date = date.today()
today_date=''.join(str(today_date).split('-'))

project_name='BUFFALO'

# database File
df=pd.read_csv('elvisbuffalony2024obweekday_export_odbc.csv')
# KingElvis Dataframe
ke_df=pd.read_excel("Buffalo_NY_OB_KINGElvis.xlsx",sheet_name='Elvis_Review')
# Details File Stops Sheet
detail_df=pd.read_excel('details_buffalo_excel_template.xlsx',sheet_name='STOPS')

df=df[df['INTERV_INIT']!='999']
df=df[df['HAVE_5_MIN_FOR_SURVECode']==1]
ke_df=ke_df[ke_df['INTERV_INIT']!='999']
ke_df=ke_df[ke_df['INTERV_INIT']!=999]
ke_df=ke_df[ke_df['HAVE_5_MIN_FOR_SURVECode']==1]
ke_df=ke_df[ke_df['Final_Usage'].str.lower()=='use']

stop_on_column_check=['stoponaddr']
stop_off_column_check=['stopoffaddr']
stop_on_id_column_check=['stoponclntid']
stop_off_id_column_check=['stopoffclntid']
stop_on_id_column=check_all_characters_present(df,stop_on_id_column_check)
stop_off_id_column=check_all_characters_present(df,stop_off_id_column_check)
stop_on_column=check_all_characters_present(df,stop_on_column_check)
stop_off_column=check_all_characters_present(df,stop_off_column_check)
route_surveyed_column_check=['routesurveyedcode']
route_surveyed_column=check_all_characters_present(ke_df,route_surveyed_column_check)
stop_on_lat_lon_columns_check=['stoponlat','stoponlong']
stop_off_lat_lon_columns_check=['stopofflat','stopofflong']
stop_on_lat_lon_columns=check_all_characters_present(df,stop_on_lat_lon_columns_check)
stop_off_lat_lon_columns=check_all_characters_present(df,stop_off_lat_lon_columns_check)
stop_off_lat_lon_columns.sort()
stop_on_lat_lon_columns.sort()


columns_to_add = ['id', *stop_off_column, *stop_on_column, *stop_off_id_column, *stop_on_id_column,*stop_off_lat_lon_columns,*stop_on_lat_lon_columns]
columns_to_add

ke_df = pd.merge(ke_df, df[columns_to_add], on='id', how='left')

new_df=ke_df.iloc[:,:]

new_df['ROUTE_SURVEYEDCode_SPLITED']=new_df['ROUTE_SURVEYEDCode'].apply(lambda x : '_'.join(str(x).split('_')[0:-1]))
detail_df['ETC_ROUTE_ID_SPLITED']=detail_df['ETC_ROUTE_ID'].apply(lambda x : '_'.join(str(x).split('_')[0:-1]))

def get_distance_between_coordinates(lat1, lon1, lat2, lon2):
    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
        
        coords_1 = (lat1, lon1)
        coords_2 = (lat2, lon2)
        
        distance = geodesic(coords_1, coords_2).miles
        return distance
    except (ValueError, TypeError) as e:
        # Handle the exception here
        print(f"Error calculating distance: {e}")  # Change to the desired distance unit


for _, row in new_df.iterrows():
    stop_on_id = row[stop_on_id_column[0]]    
    stop_off_id = row[stop_off_id_column[0]]
    stop_on_addr = row[stop_on_column[0]]    
    stop_off_addr = row[stop_off_column[0]]
    route_surveyed = row[route_surveyed_column[0]]
    
    # Using ETC_STOP_NAME to get seq_fixed value for alight_seq_df
    alight_seq_df = detail_df[
        (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
        (detail_df['ETC_STOP_NAME'].str.lower() == str(stop_off_addr).lower())
    ][['seq_fixed']]
    
    # Apply fuzzy matching for alight_seq_df if empty
    if alight_seq_df.empty:
        fuzzy_matches = process.extractOne(
            str(stop_off_addr).lower(),
            detail_df[detail_df['ETC_ROUTE_ID'] == route_surveyed]['ETC_STOP_NAME'].str.lower(),
            scorer=fuzz.ratio
        )
        if fuzzy_matches:  # Check if fuzzy_matches is not None
            best_match, score, _ = fuzzy_matches
            if score >= 90:  # Threshold for fuzzy matching
                alight_seq_df = detail_df[
                    (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
                    (detail_df['ETC_STOP_NAME'].str.lower() == best_match)
                ][['seq_fixed']]
    
    # Modify else block to calculate the nearest stop details
    if not alight_seq_df.empty:
        alight_seq = alight_seq_df.iloc[0, 0]
    else:
        stop_on_lat = row[stop_on_lat_lon_columns[0]]
        stop_on_long = row[stop_on_lat_lon_columns[1]]
        
        # Filtered data
        filtered_df = detail_df[detail_df['ETC_ROUTE_ID_SPLITED'] == row['ROUTE_SURVEYEDCode_SPLITED']][
            ['stop_lat6', 'stop_lon6', 'seq_fixed', 'ETC_STOP_ID', 'ETC_STOP_NAME']
        ]
        
        # List to store distances
        distances = []
        
        # Calculate distances for all rows in filtered_df
        for _, detail_row in filtered_df.iterrows():
            stop_lat6 = detail_row['stop_lat6']
            stop_lon6 = detail_row['stop_lon6']
            
            # Compute distance
            distance = get_distance_between_coordinates(stop_on_lat, stop_on_long, stop_lat6, stop_lon6)
            
            # Skip distance if it is 0
            if distance == 0:
                continue
            
            distances.append((distance, detail_row['seq_fixed'], detail_row['ETC_STOP_ID'], detail_row['ETC_STOP_NAME']))
        
        # Find the nearest stop (minimum distance)
        if distances:
            nearest_stop = min(distances, key=lambda x: x[0])  # x[0] is the distance
            alight_seq = nearest_stop[1]  # seq_fixed
            alight_stop_id = nearest_stop[2]  # ETC_STOP_ID
            alight_stop_name = nearest_stop[3]  # ETC_STOP_NAME
        else:
            alight_seq = 0
            alight_stop_id = None
            alight_stop_name = None

        # Update new_df with nearest stop details in new columns
        new_df.loc[row.name, stop_off_id_column[0] + '_new'] = alight_stop_id
        new_df.loc[row.name, stop_off_column[0] + '_new'] = alight_stop_name
    
    # Using ETC_STOP_NAME to get seq_fixed value for board_seq_df
    board_seq_df = detail_df[
        (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
        (detail_df['ETC_STOP_NAME'].str.lower() == str(stop_on_addr).lower())
    ][['seq_fixed']]
    
    # Apply fuzzy matching for board_seq_df if empty
    if board_seq_df.empty:
        fuzzy_matches = process.extractOne(
            str(stop_on_addr).lower(),
            detail_df[detail_df['ETC_ROUTE_ID'] == route_surveyed]['ETC_STOP_NAME'].str.lower(),
            scorer=fuzz.ratio
        )
        if fuzzy_matches:  # Check if fuzzy_matches is not None
            best_match, score, _ = fuzzy_matches
            if score >= 90:  # Threshold for fuzzy matching
                board_seq_df = detail_df[
                    (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
                    (detail_df['ETC_STOP_NAME'].str.lower() == best_match)
                ][['seq_fixed']]
    
    board_seq = board_seq_df.iloc[0, 0] if not board_seq_df.empty else 0
    
    # Update new_df with the results in new columns
    new_df.loc[row.name, 'Alight_Seq'] = alight_seq
    new_df.loc[row.name, 'Board_Seq'] = board_seq
    new_df.loc[row.name, stop_on_column[0] + '_new'] = stop_on_addr
    new_df.loc[row.name, stop_on_id_column[0] + '_new'] = stop_on_id


# previous code starts here working fine with out suffix _new in columns
# Iterate through new_df rows
# for _, row in new_df.iterrows():
#     stop_on_id = row[stop_on_id_column[0]]    
#     stop_off_id = row[stop_off_id_column[0]]
#     stop_on_addr = row[stop_on_column[0]]    
#     stop_off_addr = row[stop_off_column[0]]
#     route_surveyed = row[route_surveyed_column[0]]
    
#     # Using ETC_STOP_NAME to get seq_fixed value for alight_seq_df
#     alight_seq_df = detail_df[
#         (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
#         (detail_df['ETC_STOP_NAME'].str.lower() == str(stop_off_addr).lower())
#     ][['seq_fixed']]
    
#     # Apply fuzzy matching for alight_seq_df if empty
#     if alight_seq_df.empty:
#         fuzzy_matches = process.extractOne(
#             str(stop_off_addr).lower(),
#             detail_df[detail_df['ETC_ROUTE_ID'] == route_surveyed]['ETC_STOP_NAME'].str.lower(),
#             scorer=fuzz.ratio
#         )
#         if fuzzy_matches:  # Check if fuzzy_matches is not None
#             best_match, score, _ = fuzzy_matches
#             if score >= 90:  # Threshold for fuzzy matching
#                 alight_seq_df = detail_df[
#                     (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
#                     (detail_df['ETC_STOP_NAME'].str.lower() == best_match)
#                 ][['seq_fixed']]
    
#     # Modify else block to calculate the nearest stop details
#     if not alight_seq_df.empty:
#         alight_seq = alight_seq_df.iloc[0, 0]
#     else:
#         stop_on_lat = row[stop_on_lat_lon_columns[0]]
#         stop_on_long = row[stop_on_lat_lon_columns[1]]
        
#         # Filtered data
#         filtered_df = detail_df[detail_df['ETC_ROUTE_ID_SPLITED'] == row['ROUTE_SURVEYEDCode_SPLITED']][
#             ['stop_lat6', 'stop_lon6', 'seq_fixed', 'ETC_STOP_ID', 'ETC_STOP_NAME']
#         ]
        
#         # List to store distances
#         distances = []
        
#         # Calculate distances for all rows in filtered_df
#         for _, detail_row in filtered_df.iterrows():
#             stop_lat6 = detail_row['stop_lat6']
#             stop_lon6 = detail_row['stop_lon6']
            
#             # Compute distance
#             distance = get_distance_between_coordinates(stop_on_lat, stop_on_long, stop_lat6, stop_lon6)
            
#             # Skip distance if it is 0
#             if distance == 0:
#                 continue
            
#             distances.append((distance, detail_row['seq_fixed'], detail_row['ETC_STOP_ID'], detail_row['ETC_STOP_NAME']))
        
#         # Find the nearest stop (minimum distance)
#         if distances:
#             nearest_stop = min(distances, key=lambda x: x[0])  # x[0] is the distance
#             alight_seq = nearest_stop[1]  # seq_fixed
#             alight_stop_id = nearest_stop[2]  # ETC_STOP_ID
#             alight_stop_name = nearest_stop[3]  # ETC_STOP_NAME
#             # alight_change_seq = 0  # ETC_STOP_NAME
#         else:
#             alight_seq = 0
#             alight_stop_id = None
#             alight_stop_name = None
#             # alight_change_seq = None

#         # Update new_df with nearest stop details
#         new_df.loc[row.name, stop_off_id_column[0]] = alight_stop_id
#         new_df.loc[row.name, stop_off_column[0]] = alight_stop_name
#         # new_df.loc[row.name, 'ALIGHT_SEQ_CHANGE'] = alight_change_seq
    
#     # Using ETC_STOP_NAME to get seq_fixed value for board_seq_df
#     board_seq_df = detail_df[
#         (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
#         (detail_df['ETC_STOP_NAME'].str.lower() == str(stop_on_addr).lower())
#     ][['seq_fixed']]
    
#     # Apply fuzzy matching for board_seq_df if empty
#     if board_seq_df.empty:
#         fuzzy_matches = process.extractOne(
#             str(stop_on_addr).lower(),
#             detail_df[detail_df['ETC_ROUTE_ID'] == route_surveyed]['ETC_STOP_NAME'].str.lower(),
#             scorer=fuzz.ratio
#         )
#         if fuzzy_matches:  # Check if fuzzy_matches is not None
#             best_match, score, _ = fuzzy_matches
#             if score >= 90:  # Threshold for fuzzy matching
#                 board_seq_df = detail_df[
#                     (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
#                     (detail_df['ETC_STOP_NAME'].str.lower() == best_match)
#                 ][['seq_fixed']]
    
#     board_seq = board_seq_df.iloc[0, 0] if not board_seq_df.empty else 0
    
#     # Update new_df with the results
#     new_df.loc[row.name, 'Alight_Seq'] = alight_seq
#     new_df.loc[row.name, 'Board_Seq'] = board_seq

# Previous logic ends here working fine


# Working code using ETC_STOP_NAME and BOARDING ALIGHTING ADDRESS for Comparision
# for _, row in new_df.iterrows():
#     stop_on_id = row[stop_on_id_column[0]]    
#     stop_off_id = row[stop_off_id_column[0]]
#     stop_on_addr = row[stop_on_column[0]]    
#     stop_off_addr = row[stop_off_column[0]]
#     route_surveyed = row[route_surveyed_column[0]]
    
#     # print(stop_on_addr, stop_off_addr, route_surveyed)
    
#     # Using ETC_STOP_NAME to get seq_fixed value for alight_seq_df
#     alight_seq_df = detail_df[
#         (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
#         (detail_df['ETC_STOP_NAME'].str.lower() == str(stop_off_addr).lower())
#     ][['seq_fixed']]
    
#     # Apply fuzzy matching for alight_seq_df if empty
#     if alight_seq_df.empty:
#         fuzzy_matches = process.extractOne(
#             str(stop_off_addr).lower(),
#             detail_df[detail_df['ETC_ROUTE_ID'] == route_surveyed]['ETC_STOP_NAME'].str.lower(),
#             scorer=fuzz.ratio
#         )
#         if fuzzy_matches:  # Check if fuzzy_matches is not None
#             best_match, score, _ = fuzzy_matches
#             if score >= 90:  # Threshold for fuzzy matching
#                 alight_seq_df = detail_df[
#                     (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
#                     (detail_df['ETC_STOP_NAME'].str.lower() == best_match)
#                 ][['seq_fixed']]
    
#     alight_seq = alight_seq_df.iloc[0, 0] if not alight_seq_df.empty else 0
    
#     # Using ETC_STOP_NAME to get seq_fixed value for board_seq_df
#     board_seq_df = detail_df[
#         (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
#         (detail_df['ETC_STOP_NAME'].str.lower() == str(stop_on_addr).lower())
#     ][['seq_fixed']]
    
#     # Apply fuzzy matching for board_seq_df if empty
#     if board_seq_df.empty:
#         fuzzy_matches = process.extractOne(
#             str(stop_on_addr).lower(),
#             detail_df[detail_df['ETC_ROUTE_ID'] == route_surveyed]['ETC_STOP_NAME'].str.lower(),
#             scorer=fuzz.ratio
#         )
#         if fuzzy_matches:  # Check if fuzzy_matches is not None
#             best_match, score, _ = fuzzy_matches
#             if score >= 90:  # Threshold for fuzzy matching
#                 board_seq_df = detail_df[
#                     (detail_df['ETC_ROUTE_ID'] == route_surveyed) & 
#                     (detail_df['ETC_STOP_NAME'].str.lower() == best_match)
#                 ][['seq_fixed']]
    
#     board_seq = board_seq_df.iloc[0, 0] if not board_seq_df.empty else 0
    
#     # Update new_df with the results
#     new_df.loc[row.name, 'Alight_Seq'] = alight_seq
#     new_df.loc[row.name, 'Board_Seq'] = board_seq


new_df['SEQ_CHECK'] = new_df['Alight_Seq'] - new_df['Board_Seq']
new_df=new_df[new_df['SEQ_CHECK']<0]

ids_list = []
for idx in new_df.index:
    if new_df.loc[idx, 'SEQ_CHECK'] < 0:
        # Extract route code and modify it
        ids_list.append(new_df.loc[idx, 'id'])
        
        stop_on_id = new_df.loc[idx, stop_on_id_column[0]]  # Boarding
        stop_off_id = new_df.loc[idx, stop_off_id_column[0]]  # Alighting
        route_code = new_df.loc[idx, route_surveyed_column[0]]  # ROUTE_SURVEYEDCode

        # Modify the route code
        new_route_code = (
            f"{'_'.join(route_code.split('_')[:-1])}_01" 
            if route_code.split('_')[-1] == '00' 
            else f"{'_'.join(route_code.split('_')[:-1])}_00"
        )

        new_df.loc[idx, 'ROUTE_SURVEYEDCode_New'] = route_code
        new_df.loc[idx, 'ROUTE_SURVEYED_NEW'] = new_df.loc[idx, 'ROUTE_SURVEYED']

        new_route_name_row = detail_df[detail_df['ETC_ROUTE_ID'] == new_route_code]
        if not new_route_name_row.empty:
            new_route_name = new_route_name_row['ETC_ROUTE_NAME'].iloc[0]
            
            new_df.loc[idx, 'ROUTE_SURVEYEDCode_New'] = new_route_code
            new_df.loc[idx, 'ROUTE_SURVEYED_NEW'] = new_route_name
        else:
            print(f"New route code {new_route_code} not found in detail_df. Keeping previous values.")

new_df[['id',route_surveyed_column[0],'ROUTE_SURVEYEDCode_New','ROUTE_SURVEYED','ROUTE_SURVEYED_NEW']].to_csv('Reverse_directions.csv',index=False)

new_df.drop(columns=['ROUTE_SURVEYEDCode_SPLITED',*stop_off_lat_lon_columns,*stop_on_lat_lon_columns,'SEQ_CHECK']).to_csv(f'reviewtool_{today_date}_{project_name}_ROUTE_DIRECTION_CHECk_NewV1.csv',index=False)

print('FILE GENERATED SUCCESSFULLY')