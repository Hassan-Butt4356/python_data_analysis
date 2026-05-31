import pandas as pd
import numpy as np
from geopy.distance import geodesic
import warnings
from pprint import pprint

warnings.filterwarnings('ignore')

df=pd.read_csv('elviscota2023obweekday_export_odbc.csv')
file_name = 'COTA_KINGElvis.xlsx'
final_ke=pd.read_csv('Merged Checks.csv')
# final_ke=pd.read_excel(file_name,sheet_name='Elvis_Review')

final_ke=final_ke[final_ke['Final_Usage'].str.lower()=='use']

final_ke.rename(columns={'PREV_TRANSFERSCode':'Final_KE_PREV_TRANSFERSCode','NEXT_TRANSFERSCode':'Final_KE_NEXT_TRANSFERSCode'},inplace=True)

df = pd.merge(df, final_ke[['id','Final_KE_PREV_TRANSFERSCode','Final_KE_NEXT_TRANSFERSCode']], on='id', how='left', indicator=True)
df['Combined_ID'] = (df['_merge'] == 'both').astype(int)
# Drop the indicator column and display the resulting DataFrame
df = df.drop(columns=['_merge'])
df=df[df['Combined_ID']==1]
df.drop_duplicates(subset=['id'],inplace=True)


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
        pass
        # print(f"Error calculating distance: {e}")  # Change to the desired distance unit

df['Origin_Destin_Distance']=None
df['Boarding_Alighting_Distance']=None

origin_destin_columns_check=['originaddresslat', 'originaddresslong','destinaddresslat', 'destinaddresslong']
origin_destin_columns=check_all_characters_present(df,origin_destin_columns_check)
origin_destin_columns.sort()

'''
    origin_destin_columns=['DESTIN_ADDRESS_LAT',0
                    'DESTIN_ADDRESS_LONG',1
                    'ORIGIN_ADDRESS_LAT',2
                    'ORIGIN_ADDRESS_LONG'3
                    ]
'''


boarding_alighting_columns_check=['stoponlat', 'stoponlong', 'stopofflat', 'stopofflong']
boarding_alighting_columns=check_all_characters_present(df,boarding_alighting_columns_check)
boarding_alighting_columns.sort()

'''
    boarding_alighting_columns=[
        'STOP_OFF_LAT',0
        'STOP_OFF_LONG',1
        'STOP_ON_LAT',2
        'STOP_ON_LONG'3
        ]
'''

for index, row in df.iterrows():
    df.loc[index,'Origin_Destin_Distance']=get_distance_between_coordinates(row[origin_destin_columns[2]],row[origin_destin_columns[3]],row[origin_destin_columns[0]],row[origin_destin_columns[1]])
    df.loc[index,'Boarding_Alighting_Distance']=get_distance_between_coordinates(row[boarding_alighting_columns[2]],row[boarding_alighting_columns[3]],row[boarding_alighting_columns[0]],row[boarding_alighting_columns[1]])


def distance_check_condition(value):
    if not pd.isna(value) or value:
        if value>0.5:
            return 1
        return 0
    return 1

df['Origin_Destin_Check']=df['Origin_Destin_Distance'].apply(distance_check_condition)
df['Boarding_Alighting_Check']=df['Boarding_Alighting_Distance'].apply(distance_check_condition)

transfer_columns_check=['prevtransferscode','nexttransferscode']
transfer_columns=check_all_characters_present(df,transfer_columns_check)
transfer_columns.sort()
'''
    transfer_columns=[
        'NEXT_TRANSFERSCode',0
        'PREV_TRANSFERSCode'1
        ]
'''

# df[['Final_NEXT_TRANSFERSCode','Final_PREV_TRANSFERSCode']]=df[['Final_NEXT_TRANSFERSCode','Final_PREV_TRANSFERSCode']].fillna(0)

df['Prev_Next_Check']=None

for index,row  in df.iterrows():
    # if (row[transfer_columns[0]]==0 and pd.isna(row['Final_NEXT_TRANSFERSCode'])) and (row[transfer_columns[1]]==0 and pd.isna(row['Final_PREV_TRANSFERSCode'])):
    #     df.loc[index,'Prev_Next_Check']=0
    if row[transfer_columns[0]] ==row['Final_KE_NEXT_TRANSFERSCode'] and row[transfer_columns[1]] == row['Final_KE_PREV_TRANSFERSCode']:
        df.loc[index,'Prev_Next_Check']=0
    else:
        df.loc[index,'Prev_Next_Check']=1

# pprint(df[['Prev_Next_Check']])
# exit()


df['SUM_ALL_CHECKS']=np.where(df[['Origin_Destin_Check','Boarding_Alighting_Check','Prev_Next_Check']].any(axis=1),1,0)


df[['id',*origin_destin_columns,*boarding_alighting_columns,*transfer_columns,'Final_KE_NEXT_TRANSFERSCode','Final_KE_PREV_TRANSFERSCode','Origin_Destin_Distance','Boarding_Alighting_Distance','Origin_Destin_Check','Boarding_Alighting_Check','Prev_Next_Check','SUM_ALL_CHECKS']].to_csv("Review The Reviewer.csv",index=False)


print("File Generated SuccessFully")