import pandas as pd
import numpy as np
import copy
from geopy.distance import geodesic
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
        # print(f"Error calculating distance: {e}")  # Change to the desired distance unit
        return np.NAN
        

today_date = date.today()
today_date=''.join(str(today_date).split('-'))
project_name='GUARDIA'
df=pd.read_csv("elvislaguardia2024intercept_export_odbc.csv")

# pm_values=['PM1','PM2','PM3','PM4']
# pm_df=df[df['TIME_ONCode'].isin(pm_values)]

pm_df=copy.deepcopy(df)
pm_df=pm_df[pm_df['INTERV_INIT']!='999']
pm_df=pm_df[pm_df['HAVE_5_MIN_FOR_SURVECode']==1]

transfer_columns_checks=['prevtran1onbuslat', 'prevtran1onbuslong',
                  'prevtran1offbuslat', 'prevtran1offbuslong', 'prevtran2onbuslat', 
                  'prevtran2onbuslong', 'prevtran2offbuslat', 'prevtran2offbuslong',
                  'prevtran3onbuslat', 'prevtran3onbuslong', 'prevtran3offbuslat',
                  'prevtran3offbuslong', 'prevtran4onbuslat', 'prevtran4onbuslong', 
                  'prevtran4offbuslat', 'prevtran4offbuslong','nexttran1onbuslat',
                  'nexttran1onbuslong', 'nexttran1offbuslat', 'nexttran1offbuslong', 
                  'nexttran2onbuslat', 
                  'nexttran2onbuslong', 'nexttran2offbuslat', 'nexttran2offbuslong', 
                  'nexttran3onbuslat', 'nexttran3onbuslong',
                  'nexttran3offbuslat', 'nexttran3offbuslong', 'nexttran4onbuslat', 'nexttran4onbuslong',
                  'nexttran4offbuslat', 'nexttran4offbuslong']

transfer_columns=check_all_characters_present(pm_df,transfer_columns_checks)

transfer_route_code_check=['prevtransferscode', 'prevtransfers', 'tripfirstroutecode', 'tripsecondroutecode', 'tripthirdroutecode', 'tripfourthroutecode', 'nexttransferscode', 'nexttransfers', 'tripnextroutecode', 'tripafterroutecode', 'trip3rdroutecode', 'triplast4thrtecode']
transfer_route_code=check_all_characters_present(pm_df,transfer_route_code_check)

transfer_point_code_check=[ 'tripfirstroutecode', 'tripsecondroutecode', 'tripthirdroutecode', 'tripfourthroutecode','tripnextroutecode', 'tripafterroutecode', 'trip3rdroutecode', 'triplast4thrtecode']
transfer_point_code=check_all_characters_present(pm_df,transfer_point_code_check)

transfer_df=pm_df[['id',*transfer_route_code,*transfer_columns]]

transfer_df['PREV_TRANSFERS'].replace('(0) None',np.nan,inplace=True)
transfer_df['NEXT_TRANSFERS'].replace('(0) None',np.nan,inplace=True)

transfer_df.dropna(subset=[*transfer_point_code,*transfer_columns],how='all',inplace=True)

condition1 = (
    (transfer_df['TRIP_NEXT_ROUTECode'].notnull() |
     transfer_df['TRIP_AFTER_ROUTECode'].notnull() |
     transfer_df['TRIP_3RD_ROUTECode'].notnull() |
     transfer_df['TRIP_LAST4TH_RTECode'].notnull()) &
    transfer_df[['NEXT_TRAN_1_ON_BUS_LAT', 'NEXT_TRAN_1_ON_BUS_LONG', 'NEXT_TRAN_1_OFF_BUS_LAT',
                 'NEXT_TRAN_1_OFF_BUS_LONG', 'NEXT_TRAN_2_ON_BUS_LAT', 'NEXT_TRAN_2_ON_BUS_LONG',
                 'NEXT_TRAN_2_OFF_BUS_LAT', 'NEXT_TRAN_2_OFF_BUS_LONG', 'NEXT_TRAN_3_ON_BUS_LAT',
                 'NEXT_TRAN_3_ON_BUS_LONG', 'NEXT_TRAN_3_OFF_BUS_LAT', 'NEXT_TRAN_3_OFF_BUS_LONG',
                 'NEXT_TRAN_4_ON_BUS_LAT', 'NEXT_TRAN_4_ON_BUS_LONG', 'NEXT_TRAN_4_OFF_BUS_LAT',
                 'NEXT_TRAN_4_OFF_BUS_LONG']].isnull().all(axis=1)
)

condition2 = (
    (transfer_df['TRIP_FIRST_ROUTECode'].notnull() |
     transfer_df['TRIP_SECOND_ROUTECode'].notnull() |
     transfer_df['TRIP_THIRD_ROUTECode'].notnull() |
     transfer_df['TRIP_FOURTH_ROUTECode'].notnull()) &
    transfer_df[['PREV_TRAN_1_ON_BUS_LAT', 'PREV_TRAN_1_ON_BUS_LONG', 'PREV_TRAN_1_OFF_BUS_LAT',
                 'PREV_TRAN_1_OFF_BUS_LONG', 'PREV_TRAN_2_ON_BUS_LAT', 'PREV_TRAN_2_ON_BUS_LONG',
                 'PREV_TRAN_2_OFF_BUS_LAT', 'PREV_TRAN_2_OFF_BUS_LONG', 'PREV_TRAN_3_ON_BUS_LAT',
                 'PREV_TRAN_3_ON_BUS_LONG', 'PREV_TRAN_3_OFF_BUS_LAT', 'PREV_TRAN_3_OFF_BUS_LONG',
                 'PREV_TRAN_4_ON_BUS_LAT', 'PREV_TRAN_4_ON_BUS_LONG', 'PREV_TRAN_4_OFF_BUS_LAT',
                 'PREV_TRAN_4_OFF_BUS_LONG']].isnull().all(axis=1)
)

# Combine conditions with | (logical OR)
combined_condition = condition1 | condition2

# Filter DataFrame
filtered_df = transfer_df[combined_condition]
filtered_df['Transfer_Flag']=1

origin_destin_column_check=['originaddresslat','originaddresslong','destinaddresslat', 'destinaddresslong']
origin_destin_column=check_all_characters_present(pm_df,origin_destin_column_check)
origin_destin_column.sort()

test_df=pm_df[['id',*origin_destin_column]]

'''
origin_destin_column=['DESTIN_ADDRESS_LAT',
 'DESTIN_ADDRESS_LONG',
 'ORIGIN_ADDRESS_LAT',
 'ORIGIN_ADDRESS_LONG']

'''

for _,row in test_df.iterrows():
    test_df.loc[row.name,'Distance']=get_distance_between_coordinates(row[origin_destin_column[2]],row[origin_destin_column[3]],row[origin_destin_column[0]],row[origin_destin_column[1]])

test_df['Distance_Flag']=np.where(test_df['Distance']<0.25,1,0)
test_df=test_df[test_df['Distance_Flag']==1]

new_df=pd.merge(filtered_df,test_df[['id','Distance_Flag']],on='id',how='outer')

new_df.to_csv(f'reviewtool_{today_date}_{project_name}_OD_TRANSFER_POINTS_Checks.csv',index=False)
print("File Generated Successfully")