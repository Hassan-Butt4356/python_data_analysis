import pandas as pd
import numpy as np
from geopy.distance import geodesic
import numpy as np
import os
from datetime import date
import warnings

warnings.filterwarnings("ignore")

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

# project_name='BUFFALO'

# file_name='Buffalo_NY_OB_KINGElvis.xlsx'
# detail_df=pd.read_excel("details_buffalo_excel_template.xlsx",sheet_name='STOPS')
# df=pd.read_csv('elvisbuffalony2024obweekday_export_odbc.csv')
# elvis_df=pd.read_excel(file_name,sheet_name='Elvis_Review')


project_name='TUCSON'

file_name='Tucson_az_2025_KINGElvis.xlsx'
detail_df=pd.read_excel("details_TUCSON_AZ_od_excel.xlsx",sheet_name='STOPS')
df=pd.read_csv('elvistucson2025obweekday_export_odbc.csv')
elvis_df=pd.read_excel(file_name,sheet_name='Elvis_Review')



if file_name.split('_')[0].isdigit():
    file_first_name=file_name.split('_')[0]+'_'+file_name.split('_')[1]
else:
    file_first_name=file_name.split('_')[0]

elvis_date_check=['elvisdate']
elvis_date=check_all_characters_present(elvis_df,elvis_date_check)

df = df.merge(elvis_df[[elvis_date[0], 'id', 'Final_Usage','FINAL_REVIEWER']], on='id', how='left')

df=df[df['Final_Usage'].str.lower()=='use']

home_airport_hotel_column_names=['originaddresslat','originaddresslong', 'destinaddresslat',
                                 'destinaddresslong','originplacetype','homeaddresslat','homeaddresslong',
                                 'destinairportcode','destinplacetype']


elvis_status_column_check=['elvisstatus']
elvis_status_column=check_all_characters_present(df,elvis_status_column_check)

df=df[df['ELVIS_STATUS'].str.lower()!='delete']

def check_home_airport_hotel(df, details_df):

    # Loop through each row in the DataFrame 'df'

    data_list = check_all_characters_present(df,home_airport_hotel_column_names)
    data_list.sort()
    #['DESTIN_ADDRESS_LAT_',0
    # 'DESTIN_ADDRESS_LONG_',1
    # 'DESTIN_AIRPORT_Code_',2
    # 'DESTIN_PLACE_TYPE',3
    # 'HOME_ADDRESS_LAT_',4
    # 'HOME_ADDRESS_LONG_',5
    # 'ORIGIN_ADDRESS_LAT_',6
    # 'ORIGIN_ADDRESS_LONG_',7
    # 'ORIGIN_PLACE_TYPE']8
    for index, row in df.iterrows():
        # Extract latitude and longitude values for origin and destination

        origin_addr_lat = row[data_list[6]]
        origin_addr_lng = row[data_list[7]]
        destin_addr_lat = row[data_list[0]]
        destin_addr_lng = row[data_list[1]]

        # Check if origin latitude and longitude are missing
        if not (origin_addr_lat and origin_addr_lng):
            # Get the type of origin place
            origin_place_type = row[data_list[8]]
            lat_col, lng_col = None, None  # Initialize variables for latitude and longitude column names

            # Determine the appropriate columns based on place type
            if 'hotel' in origin_place_type.lower() or 'home' in origin_place_type.lower():
                lat_col, lng_col = data_list[4], data_list[5]
            elif 'airport' in origin_place_type.lower():
                airport_destin_code = row[data_list[2]]
                airport_row = details_df[details_df['LIME_CODE'] == airport_destin_code]
                print(airport_row)
                if not airport_row.empty:
                    lat_col, lng_col = 'lat6', 'lng6'

            # If valid latitude and longitude columns are found, populate the corresponding values
            if lat_col and lng_col:
                df.at[index, data_list[6]] = row[lat_col]
                df.at[index, data_list[7]] = row[lng_col]

        # Check if destination latitude and longitude are missing
        if not (destin_addr_lat and destin_addr_lng):
            # Get the type of destination place
            destin_place_type = row[data_list[3]]
            lat_col, lng_col = None, None  # Initialize variables for latitude and longitude column names

            # Determine the appropriate columns based on place type
            if 'hotel' in destin_place_type.lower() or 'home' in destin_place_type.lower():
                lat_col, lng_col = data_list[4], data_list[5]
            elif 'airport' in destin_place_type.lower():
                airport_destin_code = row[data_list[2]]
                airport_row = details_df[details_df['LIME_CODE'] == airport_destin_code]
                print(airport_row)
                if not airport_row.empty:
                    lat_col, lng_col = 'lat6', 'lng6'

            # If valid latitude and longitude columns are found, populate the corresponding values
            if lat_col and lng_col:
                df.at[index, data_list[0]] = row[lat_col]
                df.at[index, data_list[1]] = row[lng_col]
    # Return the DataFrame 'df' with the populated columns
    return df


# df=check_home_airport_hotel(df,detail_df)


blank_columns_checks=['originaddresslat', 'originaddresslong', 'destinaddresslat',
                      'destinaddresslong','stoponlat', 'stoponlong', 'stopofflat', 'stopofflong']
blank_column_names=check_all_characters_present(df,blank_columns_checks)



df.dropna(subset=blank_column_names, how='any',inplace=True)


boarding_columns_checks=['prevtran1onbuslat', 'prevtran1onbuslong',
                         'prevtran2onbuslat', 'prevtran2onbuslong',
                         'prevtran3onbuslat', 'prevtran3onbuslong', 
                         'prevtran4onbuslat', 
                         'prevtran4onbuslong','stoponlat', 'stoponlong',
                         'stopofflat', 'stopofflong',
                          'nexttran1offbuslat','nexttran1offbuslong',  
                         'nexttran2offbuslat', 'nexttran2offbuslong', 
                          'nexttran3offbuslat', 'nexttran3offbuslong', 
                          'nexttran4offbuslat', 'nexttran4offbuslong',]
boarding_columns=check_all_characters_present(df,boarding_columns_checks)
boarding_columns.sort()

origin_destin_columns_checks=['originaddresslat','originaddresslong', 'destinaddresslat', 'destinaddresslong']
origin_destin_columns=check_all_characters_present(df,origin_destin_columns_checks)
origin_destin_columns.sort()


df['FIRST_BOARDING_LAT']=None 
df['FIRST_BOARDING_LONG']=None
df['LAST_ALIGHTING_LAT']=None
df['LAST_ALIGHTING_LONG']=None
df['ORIGIN_TO_SURVEYBOARD']=None    #FINAL_ORIGIN_LOCATION TO STOP_ON_LOCATION (IN MILES)
df['ORIGIN_TO_FIRST_BOARD']=None    #FINAL_ORIGIN_LOCATION TO FIRST_BOARDING_LOCATION (IN MILES)
df['SURVEYBOARDING_TO_SURVEYALIGHTING']=None    #STOP_ON_LOCATION TO STOP_OFF_LOCATION (SURVEYED ROUTE) (IN MILES)
df['ORIGIN_TO_DESTINATION']=None    #FINAL_ORIGIN_LOCATION TO FINAL_DESTIN_LOCATION (IN MILES)
df['SURVEYALIGHTING_TO_DESTINATION']=None    #STOP_OFF_LOCATION TO FINAL_DESTIN LOCATION (IN MILES)
df['LAST_ALIGHTING_LOCATION_TO_DESTIN']=None   #LAST_ALIGHTING_LOCATION TO FINAL_DESTIN LOCATION (IN MILES)


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


for index, row in df.iterrows():
    if not pd.isna(row[boarding_columns[8]]) and not pd.isna(row[boarding_columns[9]]):
        #'PREV_TRAN_1_ON_BUS_LAT',
        #'PREV_TRAN_1_ON_BUS_LONG'
        df.loc[index, 'FIRST_BOARDING_LAT'] = row[boarding_columns[8]]
        df.loc[index, 'FIRST_BOARDING_LONG'] = row[boarding_columns[9]]
    elif not pd.isna(row[boarding_columns[10]]) and not pd.isna(row[boarding_columns[11]]):
        #  'PREV_TRAN_2_ON_BUS_LAT',
        # 'PREV_TRAN_2_ON_BUS_LONG'
        df.loc[index, 'FIRST_BOARDING_LAT'] = row[boarding_columns[10]]
        df.loc[index, 'FIRST_BOARDING_LONG'] = row[boarding_columns[11]]
    elif not pd.isna(row[boarding_columns[12]]) and not pd.isna(row[boarding_columns[13]]):
        #  'PREV_TRAN_3_ON_BUS_LAT',
        # 'PREV_TRAN_3_ON_BUS_LONG'
        df.loc[index, 'FIRST_BOARDING_LAT'] = row[boarding_columns[12]]
        df.loc[index, 'FIRST_BOARDING_LONG'] = row[boarding_columns[13]]
    elif not pd.isna(row[boarding_columns[14]]) and not pd.isna(row[boarding_columns[15]]):
        #  'PREV_TRAN_4_ON_BUS_LAT',
        # 'PREV_TRAN_4_ON_BUS_LONG'
        df.loc[index, 'FIRST_BOARDING_LAT'] = row[boarding_columns[14]]
        df.loc[index, 'FIRST_BOARDING_LONG'] = row[boarding_columns[15]]
    elif not pd.isna(row[boarding_columns[18]]) and not pd.isna(row[boarding_columns[19]]):
        #  'STOP_ON_LAT',
        # 'STOP_ON_LONG'
        df.loc[index, 'FIRST_BOARDING_LAT'] = row[boarding_columns[18]]
        df.loc[index, 'FIRST_BOARDING_LONG'] = row[boarding_columns[19]]
    else:
        df.loc[index, 'FIRST_BOARDING_LAT'] = np.nan
        df.loc[index, 'FIRST_BOARDING_LONG'] = np.nan
    #      
    if not pd.isna(row[boarding_columns[6]]) and not pd.isna(row[boarding_columns[7]]):
        #  'NEXT_TRAN_4_OFF_BUS_LAT',
        # 'NEXT_TRAN_4_OFF_BUS_LONG'
        df.loc[index, 'LAST_ALIGHTING_LAT'] = row[boarding_columns[6]]
        df.loc[index, 'LAST_ALIGHTING_LONG'] = row[boarding_columns[7]]
    elif not pd.isna(row[boarding_columns[4]]) and not pd.isna(row[boarding_columns[5]]):
        #  'NEXT_TRAN_3_OFF_BUS_LAT',
        # 'NEXT_TRAN_3_OFF_BUS_LONG'
        df.loc[index, 'LAST_ALIGHTING_LAT'] = row[boarding_columns[4]]
        df.loc[index, 'LAST_ALIGHTING_LONG'] = row[boarding_columns[5]]
    elif not pd.isna(row[boarding_columns[2]]) and not pd.isna(row[boarding_columns[3]]):
        #  'NEXT_TRAN_2_OFF_BUS_LAT',
        # 'NEXT_TRAN_2_OFF_BUS_LONG'
        df.loc[index, 'LAST_ALIGHTING_LAT'] = row[boarding_columns[2]]
        df.loc[index, 'LAST_ALIGHTING_LONG'] = row[boarding_columns[3]]
    elif not pd.isna(row[boarding_columns[0]]) and not pd.isna(row[boarding_columns[1]]):
        #  'NEXT_TRAN_1_OFF_BUS_LAT',
        # 'NEXT_TRAN_1_OFF_BUS_LONG'
        df.loc[index, 'LAST_ALIGHTING_LAT'] = row[boarding_columns[0]]
        df.loc[index, 'LAST_ALIGHTING_LONG'] = row[boarding_columns[1]]
    elif not pd.isna(row[boarding_columns[16]]) and not pd.isna(row[boarding_columns[17]]):
        #  'STOP_OFF_LAT',
        # 'STOP_OFF_LONG'
        df.loc[index, 'LAST_ALIGHTING_LAT'] = row[boarding_columns[16]]
        df.loc[index, 'LAST_ALIGHTING_LONG'] = row[boarding_columns[17]]
    else:
        df.loc[index, 'LAST_ALIGHTING_LAT'] = np.nan
        df.loc[index, 'LAST_ALIGHTING_LONG'] = np.nan

for index, row in df.iterrows():
    df.loc[index,'ORIGIN_TO_SURVEYBOARD']=get_distance_between_coordinates(row[origin_destin_columns[2]],row[origin_destin_columns[3]], row[boarding_columns[18]],row[boarding_columns[19]])
    df.loc[index,'ORIGIN_TO_FIRST_BOARD']=get_distance_between_coordinates(row[origin_destin_columns[2]],row[origin_destin_columns[3]],row['FIRST_BOARDING_LAT'],row['FIRST_BOARDING_LONG'])
    df.loc[index,'SURVEYBOARDING_TO_SURVEYALIGHTING']=get_distance_between_coordinates(row[boarding_columns[18]],row[boarding_columns[19]],row[boarding_columns[16]],row[boarding_columns[17]])
    df.loc[index,'ORIGIN_TO_DESTINATION']=get_distance_between_coordinates(row[origin_destin_columns[2]],row[origin_destin_columns[3]],row[origin_destin_columns[0]],row[origin_destin_columns[1]])
    df.loc[index,'SURVEYALIGHTING_TO_DESTINATION']=get_distance_between_coordinates(row[boarding_columns[16]],row[boarding_columns[17]],row[origin_destin_columns[0]],row[origin_destin_columns[1]])
    df.loc[index,'LAST_ALIGHTING_LOCATION_TO_DESTIN']=get_distance_between_coordinates(row['LAST_ALIGHTING_LAT'],row['LAST_ALIGHTING_LONG'],row[origin_destin_columns[0]],row[origin_destin_columns[1]])

df['O2B/O2D']=None   #df['ORIGIN_TO_SURVEYBOARD']/df['ORIGIN_TO_DESTINATION'] ORIGIN_TO_BOARD Divide by ORIGIN_TO_DESTINATION
df['B2A/OD']=None   #df['SURVEYBOARDING_TO_SURVEYALIGHTING']/df['ORIGIN_TO_DESTINATION'] BOARDING_TO_ALIGHTING Divide by ORIGIN_TO_DESTINATION
df['A2D/OD']=None   #df['SURVEYALIGHTING_TO_DESTINATION']/df['ORIGIN_TO_DESTINATION'] ALIGHTING_TO_DESTINATION Divide by ORIGIN_TO_DESTINATION

for index, row in df.iterrows():
    origin_to_destination = row['ORIGIN_TO_DESTINATION']
    if origin_to_destination==0:
        df.loc[index,'O2B/O2D']=0
        df.loc[index,'B2A/OD']=0
        df.loc[index,'A2D/OD']=0
    else:
        df.loc[index,'O2B/O2D']=row['ORIGIN_TO_SURVEYBOARD']/row['ORIGIN_TO_DESTINATION']
        df.loc[index,'B2A/OD']=row['SURVEYBOARDING_TO_SURVEYALIGHTING']/row['ORIGIN_TO_DESTINATION']
        df.loc[index,'A2D/OD']=row['SURVEYALIGHTING_TO_DESTINATION']/row['ORIGIN_TO_DESTINATION']

df['O_B_Dist_Check1']=None #(df['ORIGIN_TO_FIRST_BOARD'] > 1.85) & (df['ORIGIN_TRANSPORTCode'].isin(['1', '2', '-oth-']))  if [ORIGIN_TO_FIRST_BOARD]>1.85 and ORIGIN_NEW_CODE = WALK [(Text.Contains([ORIGIN_TRANSPORT],"Walk") or Text.Contains([ORIGIN_TRANSPORT],"Wheelchair") or Text.Contains([ORIGIN_TRANSPORT],"Skateboard"))]
df['O_B_Dist_Check2']=None #(df['ORIGIN_TO_FIRST_BOARD'] < 0.25) & (df['ORIGIN_TRANSPORTCode'].isin(['7', '8','9','10','11'])) if [ORIGIN_TO_FIRST_BOARD]<.25 and ORIGIN_NEW_CODE = "DRIVE" then 1 (Flag) else 0 (Non-Flag)
df['O_B_Dist_Check3']=None #(df['ORIGIN_TO_FIRST_BOARD'] < 0.25)  if [ORIGIN_TO_SURVEYBOARD]<0.25 and [#"PREV_TRANSFERS[Code]"]!="0" then 1 (Flag) else 0 (Non-Flag)


transport_transfer_columns_checks=['origintransport','destintransport','nexttransferscode','prevtransferscode']
transport_transfer_columns=check_all_characters_present(df,transport_transfer_columns_checks)
transport_transfer_columns.sort()
transport_transfer_columns

df[[transport_transfer_columns[1], transport_transfer_columns[3]]]=df[[transport_transfer_columns[1], transport_transfer_columns[3]]].fillna(0)

walk=['walk','wheelchair or scooter','other','walked','skateboard','bike, e-bike, skateboard, scooter, e-scooter','wheelchair','walked or used mobility aid']
drive=['was dropped off by someone','drove alone and parked','drove or rode with others and parked','taxi','uber, lyft, etc.',
       'get in a parked vehicle & drive alone','be picked up by someone','taxi / shuttle','get in a parked vehicle & drive, alone or w/others',
       'get in a parked vehicle & drive/ride w/others','get in a parked vehicle & drive, alone or w/others','rode with others and was dropped off',
      'rode in an uber / lyft / taxi / etc. vehicle','get in a parked vehicle & drive alone'
      ]


o_b_check1 = (df['ORIGIN_TO_FIRST_BOARD'] > 1.85) & df[transport_transfer_columns[2]].str.lower().isin(walk)
o_b_check2 = (df['ORIGIN_TO_FIRST_BOARD'] < 0.25) & df[transport_transfer_columns[2]].str.lower().isin(drive)
o_b_check3 = (df['ORIGIN_TO_SURVEYBOARD'] < 0.25) & (df[transport_transfer_columns[3]] != 0)


# # Use np.where to assign values based on conditions
df['O_B_Dist_Check1'] = np.where(o_b_check1, 1, 0)
df['O_B_Dist_Check2'] = np.where(o_b_check2, 1, 0)
df['O_B_Dist_Check3'] = np.where(o_b_check3, 1, 0)

df['A_D_Dist_Check1']=None #(df['LAST_ALIGHTING_LOCATION_TO_DESTIN'] > 1.85) & (df['ORIGIN_TRANSPORTCode'].isin(['1', '2', '-oth-']))  if [ORIGIN_TO_FIRST_BOARD]>1.85 and ORIGIN_NEW_CODE = WALK [(Text.Contains([ORIGIN_TRANSPORT],"Walk") or Text.Contains([ORIGIN_TRANSPORT],"Wheelchair") or Text.Contains([ORIGIN_TRANSPORT],"Skateboard"))]
df['A_D_Dist_Check2']=None #(df['LAST_ALIGHTING_LOCATION_TO_DESTIN'] < 0.25) & (df['ORIGIN_TRANSPORTCode'].isin(['7', '8','9','10','11'])) if [ORIGIN_TO_FIRST_BOARD]<.25 and ORIGIN_NEW_CODE = "DRIVE" then 1 (Flag) else 0 (Non-Flag)
df['A_D_Dist_Check3']=None #(df['SURVEYALIGHTING_TO_DESTINATION'] < 0.25)  if [SURVEYALIGHTING_TO_DESTINATION]<0.25 and [#"NEXT_TRANSFERS[Code]"]!="0" then 1 (Flag) else 0 (Non-Flag)


a_d_check1 = (df['LAST_ALIGHTING_LOCATION_TO_DESTIN'] > 1.85) & df[transport_transfer_columns[0]].isin(walk)
a_d_check2 = (df['LAST_ALIGHTING_LOCATION_TO_DESTIN'] < 0.25) & df[transport_transfer_columns[0]].isin(drive)
a_d_check3 = (df['SURVEYALIGHTING_TO_DESTINATION'] < 0.25) & (df[transport_transfer_columns[1]] != 0)

# # Use np.where to assign values based on conditions
df['A_D_Dist_Check1'] = np.where(a_d_check1, 1, 0)
df['A_D_Dist_Check2'] = np.where(a_d_check2, 1, 0)
df['A_D_Dist_Check3'] = np.where(a_d_check3, 1, 0)

df['O_D_Dist_Check1']=None #if [ORIGIN_TO_DESTINATION]<0.05 then 1 else 0 =DELETE
df['O_D_Dist_Check2']=None # if [ORIGIN_TO_DESTINATION]<0.25 then 1 else 0) = REVIEW
df['O_D_Dist_Check3']=None # if [ORIGIN_TO_DESTINATION]>50 then 1 else 0) = REVIEW

# Create boolean arrays for each condition
o_d_check1 = df['ORIGIN_TO_DESTINATION'] < 0.05
o_d_check2 = df['ORIGIN_TO_DESTINATION'] < 0.25
o_d_check3 = df['ORIGIN_TO_DESTINATION'] > 50

# Use np.where to assign values based on conditions
df['O_D_Dist_Check1'] = np.where(o_d_check1, 1, 0)
df['O_D_Dist_Check2'] = np.where(o_d_check2, 1, 0)
df['O_D_Dist_Check3'] = np.where(o_d_check3, 1, 0)

df['B_A_Dist_Check1']=None #if ["B2A/OD"]>1.75 then 1 (Flag) else 0 (Non-Flag)
df['B_A_Dist_Check2']=None #if [#"B2A/OD"]<0.45 and ORIGIN_NEW_CODE = "WALK" and DESTIN_NEW_CODE = "WALK"([#"PREV_TRANSFERS[Code]"]="0" and [#"NEXT_TRANSFERS[Code]"]="0") then 1 (Flag) else 0 (Non-Flag)

# for index,row in df.iterrows():
b_a_check1=df['B2A/OD']>1.75
b_a_check2=(df['B2A/OD']<0.45)&(df[transport_transfer_columns[2]].isin(walk))&(df[transport_transfer_columns[0]].isin(walk))&(df[transport_transfer_columns[1]]==0)&(df[transport_transfer_columns[3]]==0)

df['B_A_Dist_Check1']=np.where(b_a_check1,1,0)
df['B_A_Dist_Check2']=np.where(b_a_check2,1,0)


# for _, row in df[['O_B_Dist_Check1', 'O_B_Dist_Check2', 'O_B_Dist_Check3',
#                   'A_D_Dist_Check1', 'A_D_Dist_Check2', 'A_D_Dist_Check3',
#                   'O_D_Dist_Check1', 'O_D_Dist_Check2', 'O_D_Dist_Check3',
#                   'B_A_Dist_Check1', 'B_A_Dist_Check2']].iterrows():
#     if row['O_B_Dist_Check1'] == 1:
#         description = 'Origin to Board distance is greater than 1.85 miles, and Access Mode is Walk.'
#     elif row['O_B_Dist_Check2'] == 1:
#         description = 'Origin to Board distance is less than 0.25 miles, and Access Mode is not Walk.'
#     elif row['O_B_Dist_Check3'] == 1:
#         description = 'Origin to Board distance is less than 0.25 miles, and Previous Transfers are present.'
#     elif row['A_D_Dist_Check1'] == 1:
#         description = 'Last Alighting to Destination distance is greater than 1.85 miles, and Egress Mode is Walk.'
#     elif row['A_D_Dist_Check2'] == 1:
#         description = 'Last Alighting to Destination distance is less than 0.25 miles, and Egress Mode is not Walk.'
#     elif row['A_D_Dist_Check3'] == 1:
#         description = 'Survey Alighting to Destination distance is less than 0.25 miles, and Next Transfers are present.'
#     elif row['O_D_Dist_Check1'] == 1:
#         description = 'Origin to Destination distance is less than 0.05 miles.'
#     elif row['O_D_Dist_Check2'] == 1:
#         description = 'Origin to Destination distance is less than 0.25 miles.'
#     elif row['O_D_Dist_Check3'] == 1:
#         description = 'Origin to Destination distance is greater than 50 miles.'
#     elif row['B_A_Dist_Check1'] == 1:
#         description = 'B2A/OD (Boarding to Alighting divided by Origin to Destination) is greater than 1.75 miles.'
#     elif row['B_A_Dist_Check2'] == 1:
#         description = 'B2A/OD (Boarding to Alighting divided by Origin to Destination) is less than 0.45 miles, and Access and Egress Mode is Walk, with no Next or Previous transfers.'
#     else:
#         description = 'No issues detected.'

#     df.loc[row.name, 'O_D_Distance_Flag_Description'] = description

for _, row in df[['O_B_Dist_Check1', 'O_B_Dist_Check2', 'O_B_Dist_Check3',
                  'A_D_Dist_Check1', 'A_D_Dist_Check2', 'A_D_Dist_Check3',
                  'O_D_Dist_Check1', 'O_D_Dist_Check2', 'O_D_Dist_Check3',
                  'B_A_Dist_Check1', 'B_A_Dist_Check2']].iterrows():
    descriptions = []

    if row['O_B_Dist_Check1'] == 1:
        descriptions.append('Origin to Board distance is greater than 1.85 miles, and Access Mode is Walk.')
    if row['O_B_Dist_Check2'] == 1:
        descriptions.append('Origin to Board distance is less than 0.25 miles, and Access Mode is not Walk.')
    if row['O_B_Dist_Check3'] == 1:
        descriptions.append('Origin to Board distance is less than 0.25 miles, and Previous Transfers are present.')
    if row['A_D_Dist_Check1'] == 1:
        descriptions.append('Last Alighting to Destination distance is greater than 1.85 miles, and Egress Mode is Walk.')
    if row['A_D_Dist_Check2'] == 1:
        descriptions.append('Last Alighting to Destination distance is less than 0.25 miles, and Egress Mode is not Walk.')
    if row['A_D_Dist_Check3'] == 1:
        descriptions.append('Survey Alighting to Destination distance is less than 0.25 miles, and Next Transfers are present.')
    if row['O_D_Dist_Check1'] == 1:
        descriptions.append('Origin to Destination distance is less than 0.05 miles.')
    if row['O_D_Dist_Check2'] == 1:
        descriptions.append('Origin to Destination distance is less than 0.25 miles.')
    if row['O_D_Dist_Check3'] == 1:
        descriptions.append('Origin to Destination distance is greater than 50 miles.')
    if row['B_A_Dist_Check1'] == 1:
        descriptions.append('B2A/OD (Boarding to Alighting divided by Origin to Destination) is greater than 1.75 miles.')
    if row['B_A_Dist_Check2'] == 1:
        descriptions.append('B2A/OD (Boarding to Alighting divided by Origin to Destination) is less than 0.45 miles, and Access and Egress Mode is Walk, with no Next or Previous transfers.')

    if descriptions:
        df.loc[row.name, 'O_D_Distance_Flag_Description'] = ' '.join(descriptions)
    else:
        df.loc[row.name, 'O_D_Distance_Flag_Description'] = 'No issues detected.'


df['SUM_ALL_CHECKS']=np.where(df[['O_B_Dist_Check1','O_B_Dist_Check2','O_B_Dist_Check3','A_D_Dist_Check1','A_D_Dist_Check2','A_D_Dist_Check3','O_D_Dist_Check1','O_D_Dist_Check2','O_D_Dist_Check3','B_A_Dist_Check1','B_A_Dist_Check2']].any(axis=1),1,0)

# print(df[df['SUM_ALL_CHECKS']==1])


powerbi_columns_checks=['id',
                        'homeaddresscity','homeaddresszip','homeaddresslat',
                        'homeaddresslong','homeaddressaddr','homeaddressplace','homeaddressstate',
                        'originplacetypecode','originplacetype','originaddressaddr','originaddresscity',
                        'originaddressstate','originaddresszip','originaddresslat','originaddresslong','origintransport',
                        'destinplacetypecode','destinplacetype','destinaddressaddr','destinaddresscity',
                        'destinaddressstate','destinaddresszip','destinaddresslat','destinaddresslong',
                       'destintransport','routesurveyedcode','routesurveyed']
powerbi_columns=check_all_characters_present(df,powerbi_columns_checks)

# powerbi_columns
new_df_columns=['FINAL_REVIEWER','ORIGIN_TO_SURVEYBOARD','ORIGIN_TO_FIRST_BOARD','SURVEYBOARDING_TO_SURVEYALIGHTING','ORIGIN_TO_DESTINATION','SURVEYALIGHTING_TO_DESTINATION','LAST_ALIGHTING_LOCATION_TO_DESTIN','O2B/O2D','B2A/OD','A2D/OD','O_B_Dist_Check1','O_B_Dist_Check2','O_B_Dist_Check3','A_D_Dist_Check1','A_D_Dist_Check2','A_D_Dist_Check3','O_D_Dist_Check1','O_D_Dist_Check2','O_D_Dist_Check3','B_A_Dist_Check1','B_A_Dist_Check2','O_D_Distance_Flag_Description','SUM_ALL_CHECKS']
distance_checks_columns=[*powerbi_columns,*boarding_columns,*origin_destin_columns,*transport_transfer_columns,*new_df_columns]

od_df=df[distance_checks_columns]

od_df = od_df.rename(columns={od_df.columns[1]: 'Final_Direction_Code', od_df.columns[2]: 'Final_Direction'})
od_df.drop_duplicates(subset='id', keep='first', inplace=True)


od_df[od_df['SUM_ALL_CHECKS']==1].to_csv(f'reviewtool_{today_date}_{project_name}_OD_Distance_Checks.csv',index=False)
# od_df[od_df['SUM_ALL_CHECKS']==1].to_csv(f'{file_first_name}_OD_Distance_Checks(v{version}).csv',index=False)

print("#####################################################################")
print(f'File Created SuccessFully')
print("#####################################################################")