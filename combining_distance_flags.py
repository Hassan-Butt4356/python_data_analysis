import pandas as pd
import warnings
import numpy as np
import copy
from datetime import date

warnings.filterwarnings("ignore")

# project_name='ANCHORAGE'

# file_name='ANCHORAGE_AK_KINGElvis (2).xlsx'
# detail_df=pd.read_excel("details_anchorage_ak_od_excel (3).xlsx",sheet_name='STOPS')
# df=pd.read_csv('elvisanchorageak2024obweekday_export_odbc.csv')
# elvis_df=pd.read_excel(file_name,sheet_name='Elvis_Review')

project_name='TUCSON'

file_name='Tucson_az_2025_KINGElvis.xlsx'
detail_df=pd.read_excel("details_TUCSON_AZ_od_excel.xlsx",sheet_name='STOPS')
df=pd.read_csv('elvistucson2025obweekday_export_odbc.csv')
elvis_df=pd.read_excel(file_name,sheet_name='Elvis_Review')


today_date = date.today()
today_date=''.join(str(today_date).split('-'))

# Database file if you want to add origin destin board and alighting lat longs in the combined flag files
database_df=pd.read_csv('elvistucson2025obweekday_export_odbc.csv')

# elvis_df=pd.read_csv(file_name)
elvis_df=pd.read_excel(file_name,sheet_name='Elvis_Review')

try:
    traditional_df=pd.read_csv(f'reviewtool_{today_date}_{project_name}_TraditionalTransferFlags.csv')
except:
    traditional_df=pd.DataFrame()
try:
    od_df=pd.read_csv(f'reviewtool_{today_date}_{project_name}_OD_Distance_Checks.csv')
except:
    od_df=pd.DataFrame()
try:
    transfer_df=pd.read_csv(f'reviewtool_{today_date}_{project_name}_Distance_Transfer_Flags.csv')
except:
    transfer_df=pd.DataFrame()
# recovery_df=pd.read_excel('COTA_survey_recovery_2023-12-06.xlsx', sheet_name='_(F0) SURVEY RECOVERY')

# get data where Final_Usage== 'use'
# elvis_df=elvis_df[elvis_df['Final_Usage'].str.lower()=='use']

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



if not traditional_df.empty:
    # merge Traditional Transfer Checks with KingELvis Data
    merged_df = pd.merge(elvis_df, traditional_df['id'], on='id', how='left', indicator=True)
    # Create a new column 'Traditional_Check' based on the merge indicator
    merged_df['Traditional_Check'] = (merged_df['_merge'] == 'both').astype(int)
    # Drop the indicator column and display the resulting DataFrame
    merged_df = merged_df.drop(columns=['_merge'])
else:
    merged_df=copy.deepcopy(elvis_df)
    merged_df['Traditional_Check']=0


# # merge Recovery Transfer Checks with KingELvis Data
# merged_df = pd.merge(merged_df, recovery_df['id'], on='id', how='left', indicator=True)
# # Create a new column 'Traditional_Check' based on the merge indicator
# merged_df['Recovery_Check'] = (merged_df['_merge'] == 'both').astype(int)
# # Drop the indicator column and display the resulting DataFrame
# merged_df = merged_df.drop(columns=['_merge'])

if not od_df.empty:
    # merge OD Distance Transfer Checks with Merged Data of Traditional Checks
    merged_df = pd.merge(merged_df, od_df[['id','O_D_Distance_Flag_Description']], on='id', how='left', indicator=True)
    # Create a new column 'OD_Distance_Check' based on the merge indicator
    merged_df['OD_Distance_Check'] = (merged_df['_merge'] == 'both').astype(int)
    # Drop the indicator column and display the resulting DataFrame
    merged_df = merged_df.drop(columns=['_merge'])
else:
    merged_df['OD_Distance_Check']=0

if not transfer_df.empty:
    # merge TRansfer Distance Checks with Merged Data of Traditional and OD Distance Checks
    merged_df = pd.merge(merged_df, transfer_df[['id','Transfer_Distance_Flag_Description']], on='id', how='left', indicator=True)
    # Create a new column 'Transfer_Distance_Check' based on the merge indicator
    merged_df['Transfer_Distance_Check'] = (merged_df['_merge'] == 'both').astype(int)
    # Drop the indicator column and display the resulting DataFrame
    merged_df = merged_df.drop(columns=['_merge'])
else:
    merged_df['Transfer_Distance_Check']=0

# merged_df=merged_df[(merged_df['Transfer_Distance_Check']==1)  | (merged_df['OD_Distance_Check']==1) | (merged_df['Traditional_Check']==1)]

flag_description_columns_check=['oddistanceflagdescription','transferdistanceflagdescription']
flag_description_columns=check_all_characters_present(merged_df,flag_description_columns_check)

if flag_description_columns:
    for _,row in merged_df.iterrows():
        if not pd.isna(row['O_D_Distance_Flag_Description']) and not pd.isna(row['Transfer_Distance_Flag_Description']):
            merged_df.loc[row.name,'Flag Description']=row['O_D_Distance_Flag_Description'] +' '+ row['Transfer_Distance_Flag_Description']
        elif not pd.isna(row['O_D_Distance_Flag_Description']):
            merged_df.loc[row.name,'Flag Description']=row['O_D_Distance_Flag_Description']
        elif not pd.isna(row['Transfer_Distance_Flag_Description']):
            merged_df.loc[row.name,'Flag Description']= row['Transfer_Distance_Flag_Description']
        else:
            merged_df.loc[row.name,'Flag Description']=' '
else:
    merged_df['Flag Description']=' '

merged_df.drop(columns=['Transfer_Distance_Flag_Description','O_D_Distance_Flag_Description'],inplace=True)

review_columns_check=['2xreviewcheck','2X_REVIEW_CHECK.1']

review_columns=check_all_characters_present(elvis_df,review_columns_check)

if review_columns:
    # create new column where all checks are 1
    merged_df.drop(columns=[*review_columns],inplace=True)
    merged_df['2X_REVIEW_CHECK']=np.where(merged_df[['Transfer_Distance_Check','OD_Distance_Check','Traditional_Check']].any(axis=1),1,0)
    # merged_df['2X_REVIEW_CHECK']=np.where(merged_df[['Transfer_Distance_Check','OD_Distance_Check','Traditional_Check','Recovery_Check']].any(axis=1),1,0)
else:
    merged_df['2X_REVIEW_CHECK']=np.where(merged_df[['Transfer_Distance_Check','OD_Distance_Check','Traditional_Check']].any(axis=1),1,0)
    # create new empty columns
    merged_df['2x_REVIEWED_BY']=None
    merged_df['2x_REVIEWED_FLAG']=None
    merged_df['ADMIN_APPROVED']=None

# merged_df[merged_df['2X_REVIEW_CHECK']==1].to_csv('Merged Checks.csv',index=False)

merged_df.drop_duplicates(subset=['id'],inplace=True)


# Code to add Origin Destin Boarding and Alighting columns to the  mid of the combined Flag file
# od_ba_names_check=['originaddresslat', 'originaddresslong', 'stoponlat', 'stoponlong', 'stopofflat', 'stopofflong', 'destinaddresslat', 'destinaddresslong']
# od_ba_names=check_all_characters_present(database_df,od_ba_names_check)

# merged_df=pd.merge(merged_df,database_df[['id',*od_ba_names]],on='id',how='left')

# cols = list(merged_df.columns)

# # Step 3: Remove the new columns from their current position
# for col in od_ba_names:
#     cols.remove(col)

# insert_position = 3

# # Step 5: Insert the new columns into the desired position
# for col in reversed(od_ba_names):  # reversed to maintain order when inserting
#     cols.insert(insert_position, col)

# merged_df = merged_df[cols]

# here the code is finished to add Origin Destin Boarding and Alighting columns to the  mid of the combined Flag file

merged_df.to_csv(f'reviewtool_{today_date}_{project_name}_combinedflags.csv',index=False)
# merged_df.to_csv('MUNI Merged Checks(v2).csv',index=False)

print('File Generated Successfully')