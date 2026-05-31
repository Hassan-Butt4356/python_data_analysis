import pandas as pd
import numpy as np
from math import sin, cos, sqrt, atan2, radians
from global_land_mask import globe
from urllib.parse import urlencode
import math
import datetime
import xlsxwriter
import datetime
from helper import *
today = datetime.date.today()

import warnings
warnings.filterwarnings('ignore')

# file_name = 'RENO_KINGElvis (6).xlsx'
# detail_df=pd.read_excel("details_project_od_RENO (3).xlsx",sheet_name='STOPS')
# df=pd.read_csv('elvisreno_od2023_weekday_export_odbc(V1).csv')
# elvis_df=pd.read_excel(file_name,sheet_name='Elvis_Review')
# elvis_df=pd.read_csv('COTA_KINGElvis.csv')

municipality = 'UTA'
file_name='UTA_SLC_KINGElvis (1).xlsx'
detail_df=pd.read_excel("details_project_od_excel_UTA (2).xlsx",sheet_name='STOPS')
df=pd.read_csv('elvisutaobweekday2024_export_odbc(v1).csv')
elvis_df=pd.read_excel(file_name,sheet_name='Elvis_Review')


def remove_test_records(df):
    df = df[df['INTERV_INIT']!=999]
    return df

df=remove_test_records(df)
elvis_df=remove_test_records(elvis_df)

def get_removal_marked_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get rows from a DataFrame where 'Final_Usage' or 'FINAL_USAGE' is marked as 'Remove' or 'remove'.
    
    Args:
        df (pd.DataFrame): Input DataFrame
    
    Returns:
        pd.DataFrame: DataFrame containing the rows that should be removed
    """
    # Using the 'isin' function to check multiple values at once and casefold for case-insensitive matching
    columns_to_check = ['Final_Usage', 'FINAL_USAGE']
    
    for column in columns_to_check:
        if column in df.columns:
            return df[df[column].apply(lambda x: str(x).casefold()) == 'remove']
    
    return pd.DataFrame()

df_removals = get_removal_marked_records(elvis_df)

def haversine_distance(coord1, coord2):
    R = 3958.8  # Radius of the Earth in miles
    try:
        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    except:
        return 10000000
    try:
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    except:
        lat2, lon2 = coord2.split(',')
        lat2, lon2 = radians(float(lat2)), radians(float(lon2))
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


def filter_df_by_ids(df, removals_df, column_name='id'):
    """
    Filters a DataFrame based on a list of IDs from another DataFrame.

    Parameters:
        df (DataFrame): The DataFrame to be filtered.
        removals_df (DataFrame): The DataFrame containing IDs to filter out.
        column_name (str): The name of the column containing the IDs.

    Returns:
        DataFrame: A filtered DataFrame containing only the rows with IDs in removals_df.
    """
    removal_ids = removals_df[column_name]
    filtered_df = df[df[column_name].isin(removal_ids)]
    return filtered_df

df_removals = filter_df_by_ids(df, df_removals)


def get_boarding_points(cord_df):
    here_boarding_points = []  # List to store boarding points
    print("Processing Routes...")
    
    for index, cord in cord_df.iterrows():
        
        # Initialize to None, in case the second pair doesn't exist
        second_pair = None

        # Search for second pair of coordinates if available
        lat_cols = [col for col in cord_df.columns if '_LAT' in col and col not in ['ORIGIN_ADDRESS_LAT', 'DESTIN_ADDRESS_LAT']]
        long_cols = [col.replace('_LAT', '_LONG') for col in lat_cols]
        
        if len(lat_cols) > 1:
            lat = cord.get(lat_cols[1])
            long = cord.get(long_cols[1])
            
            if not pd.isna(lat) and not pd.isna(long):
                if lat not in [',', ''] and long not in [',', '']:
                    second_pair = (lat, long)

        here_boarding_points.append(second_pair)
    
    # Add the boarding points to the DataFrame
    cord_df['here_boarding_point'] = here_boarding_points
    
    return cord_df


def evaluate_removal_conditions(df):
    # Initialize empty lists to store values for each new column
    REVIEW_REVIEWER = []
    REVIEW_USAGE = []
    FLAG_ALL_EQUAL = []
    FLAG_POSS_HD = []
    FLAG_POSS_TRAN = []
    FLAG_WATER_ORIGIN = []  # Flag for origin in water
    FLAG_WATER_DESTIN = []  # Flag for destination in water
    def sanitize_coordinates(lat, lon):
        # Ensure latitude is within [-90, 90]
        lat = max(min(lat, 90), -90)
        # Ensure longitude is within [-180, 180]
        lon = (lon + 180) % 360 - 180
        return lat, lon

    for index, row in df.iterrows():
        HOME = row['HOME_ADDRESS_LAT'], row['HOME_ADDRESS_LONG']
        # Check for NaN values in ORIGIN and DESTIN
        ORIGIN = None if math.isnan(row['ORIGIN_ADDRESS_LAT']) or math.isnan(row['ORIGIN_ADDRESS_LONG']) else (row['ORIGIN_ADDRESS_LAT'], row['ORIGIN_ADDRESS_LONG'])
        DESTIN = None if math.isnan(row['DESTIN_ADDRESS_LAT']) or math.isnan(row['DESTIN_ADDRESS_LONG']) else (row['DESTIN_ADDRESS_LAT'], row['DESTIN_ADDRESS_LONG'])
        
        BOARDING = row['here_boarding_point']
        
        # Set common REVIEW_REVIEWER
        REVIEW_REVIEWER.append("Recovery Script")

        # Check if ORIGIN or DESTIN are in a body of water using global_land_mask, if they are not None
        is_origin_water = not globe.is_land(*ORIGIN) if ORIGIN is not None else False
        is_destin_water = not globe.is_land(*DESTIN) if DESTIN is not None else False
        FLAG_WATER_ORIGIN.append(is_origin_water)
        FLAG_WATER_DESTIN.append(is_destin_water)
       

        # Three matching points
        if HOME == ORIGIN and HOME == DESTIN and ORIGIN == DESTIN:
            REVIEW_USAGE.append('Remove')
            FLAG_ALL_EQUAL.append(True)
            FLAG_POSS_HD.append(False)
            FLAG_POSS_TRAN.append(False)
        elif is_origin_water or is_destin_water:
            REVIEW_USAGE.append('REVIEW')
            FLAG_ALL_EQUAL.append(False)
            FLAG_POSS_HD.append(False)
            FLAG_POSS_TRAN.append(False)
        # Home possible origin or destination
        elif ORIGIN == DESTIN and (HOME != ORIGIN or HOME != DESTIN) and (HOME != None) and (DESTIN != None):
            REVIEW_USAGE.append('REVIEW')  # 'Use' changed to 'REVIEW'
            FLAG_ALL_EQUAL.append(False)
            FLAG_POSS_HD.append(True)
            FLAG_POSS_TRAN.append(False)
        
        # Possible transfer case
        else:
            # 'Use' changed to 'REVIEW'
            FLAG_ALL_EQUAL.append(False)
            FLAG_POSS_HD.append(False)
            
            if BOARDING is not None and haversine_distance(ORIGIN, BOARDING) > 2:
                FLAG_POSS_TRAN.append(True)
                REVIEW_USAGE.append('REVIEW')
            else:
                FLAG_POSS_TRAN.append(False)
                REVIEW_USAGE.append('Remove')
             

    # Add new columns to the DataFrame
    df['REVIEW_REVIEWER'] = REVIEW_REVIEWER
    df['REVIEW_USAGE'] = REVIEW_USAGE
    df['FLAG_ALL_EQUAL'] = FLAG_ALL_EQUAL
    df['FLAG_POSS_HD'] = FLAG_POSS_HD
    df['FLAG_POSS_TRAN'] = FLAG_POSS_TRAN
    df['FLAG_WATER_ORIGIN'] = FLAG_WATER_ORIGIN  # Adding new flag column for ORIGIN
    df['FLAG_WATER_DESTIN'] = FLAG_WATER_DESTIN  # Adding new flag column for DESTIN
    flag_columns = ['FLAG_ALL_EQUAL', 'FLAG_POSS_HD', 'FLAG_POSS_TRAN', 'FLAG_WATER_ORIGIN', 'FLAG_WATER_DESTIN']

    # Convert each flag column to integer type
    for col in flag_columns:
        df[col] = df[col].astype(int)
    # Select only the columns you want to keep in the final DataFrame
    return df[['REVIEW_REVIEWER', 'REVIEW_USAGE', 'Date_started', 'id', 'FLAG_ALL_EQUAL', 'FLAG_POSS_HD', 'FLAG_POSS_TRAN', 'FLAG_WATER_ORIGIN', 'FLAG_WATER_DESTIN']]

def make_survey_recovery_sheet(excel_path, df):
    # Generate a unique name for the new workbook using a timestamp
    #current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    excel_path = f"{excel_path}.xlsx"
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        # Write the DataFrame to the Excel workbook
        df[df['Recovery_Flags']==1].to_excel(writer, sheet_name='_(F0) SURVEY RECOVERY',index=False)

bp_df = get_boarding_points(df_removals)
recovery_df = evaluate_removal_conditions(bp_df)
recovery_df['Recovery_Flags']=np.where(recovery_df[['FLAG_ALL_EQUAL', 'FLAG_POSS_HD', 'FLAG_POSS_TRAN', 'FLAG_WATER_ORIGIN', 'FLAG_WATER_DESTIN']].any(axis=1),1,0)
make_survey_recovery_sheet(f'{municipality}_survey_recovery_{today}', recovery_df)

print('Recovery File Generated Successfully')


# Fixing Past Recovery


df = pd.read_excel(f'{municipality}_survey_recovery_{today}.xlsx')



# if REVIEW_USAGE == 'Remove' then drop that row
if 'REVIEW_USAGE' in df.columns:
    df = df[df['REVIEW_USAGE'] != 'Remove']
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

# Rename REVIEW_REVIEWER to 1st Reviewer
df = df.rename(columns={'REVIEW_REVIEWER': '1st Reviewer'})
# Rename REVIEW_USAGE to 1st Reviewer Usage
df = df.rename(columns={'REVIEW_USAGE': '1st Reviewer Usage'})

#For df, add ROUTE_SURVEYEDCode from bct_ke
df = df.merge(elvis_df[['id', 'ROUTE_SURVEYEDCode']], on='id', how='left')

#For df, add ELVIS_STATUS from bct_ke
df = df.merge(elvis_df[['id', 'ELVIS_STATUS']], on='id', how='left')



# Add a column at the beginning of the DataFrame for the 2nd Reviewer
df.insert(0, '2nd Reviewer', None)
# Add a column at the beginning of the DataFrame for the 2nd Reviewer Usage 
df.insert(1, '2nd Reviewer Usage', None)
df.insert(2, 'Final_Usage', None)

# Move ROUTE_SURVEYEDCode to the beginning of the dataframe
df = df[['ROUTE_SURVEYEDCode'] + [col for col in df.columns if col != 'ROUTE_SURVEYEDCode']]

# Make "ELVIS_STATUS" the sixth column of the dataframe


# Remove duplicates from the dataframe based on elvis_id, while removing the first instance
df = df.drop_duplicates(subset=['id'], keep='last')

upper_municipality = municipality.upper()

df.to_csv(f'{upper_municipality}_KINGElvis_recovery_revised_{today}.csv', index=False)