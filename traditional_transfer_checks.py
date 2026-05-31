import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from concurrent.futures import ThreadPoolExecutor
from icecream import ic
import os
import numpy as np
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


# Only for Denver

# prev_transfer_code_columns=['tripfirstroutecode','tripsecondroutecode','tripthirdroutecode','tripfourthroutecode']
# next_transfer_code_columns=['tripnextroutecode','tripafterroutecode','trip3rdroutecode','triplast4thrtecode']
# prev_transfer_code_columns=check_all_characters_present(df,prev_transfer_code_columns)
# next_transfer_code_columns=check_all_characters_present(df,next_transfer_code_columns)
# def transform_code(value):
#     if not value or pd.isna(value):  # Check for None, empty string, or NaN
#         return np.nan
#     return '_'.join([x for i, x in enumerate(str(value).split('_')) if i != 1])

# # List of columns that need the transformation
# all_columns = ['ROUTE_SURVEYEDCode'] + prev_transfer_code_columns + next_transfer_code_columns

# # Apply the transformation to each specified column
# for col in all_columns:
#     df[col] = df[col].apply(transform_code)

# # df['ROUTE_SURVEYEDCode']=df['ROUTE_SURVEYEDCode'].apply(lambda a: '_'.join([x for i, x in enumerate(a.split('_')) if i != 1]))
# detail_df['ETC_ROUTE_ID']=detail_df['ETC_ROUTE_ID'].apply(lambda a: '_'.join([x for i, x in enumerate(a.split('_')) if i != 1]))

# DENVER Specific code end here 


if file_name.split('_')[0].isdigit():
    file_first_name=file_name.split('_')[0]+'_'+file_name.split('_')[1]
else:
    file_first_name=file_name.split('_')[0]

elvis_date_check=['elvisdate']
elvis_date=check_all_characters_present(elvis_df,elvis_date_check)

# df = df.merge(elvis_df[['elvis_date', 'id', 'Final_Usage']], on='id', how='left')
df = df.merge(elvis_df[[elvis_date[0], 'id', 'Final_Usage','FINAL_REVIEWER']], on='id', how='left')

# latest_date = pd.to_datetime(df['Elvis_Date']).max()

# df = df[df['id'] > 14165]

elvis_status_column_check=['elvisstatus']
elvis_status_column=check_all_characters_present(df,elvis_status_column_check)

df=df[df[elvis_status_column[0]].str.lower()!='delete']

df=df[df['Final_Usage'].str.lower()=='use']
# df=df[(df['Elvis_Date']==latest_date)& (df['Final_Usage'].str.lower()=='use')]

# Check the duplicates
# ROUTE_SURVEYED[Code]
duplicate_records_checks=['routesurveyedcode','prevtran1onbuslat', 'prevtran1onbuslong',
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
duplicate_columns=check_all_characters_present(df,duplicate_records_checks)
duplicates = df.drop_duplicates(subset=duplicate_columns)


# PREV and NEXT transfer should match the route name
prev_transfer_codes=['prevtransferscode','tripfirstroutecode','tripsecondroutecode','tripthirdroutecode','tripfourthroutecode']
next_transfer_codes=['nexttransferscode','tripnextroutecode','tripafterroutecode','trip3rdroutecode','triplast4thrtecode']
prev_transfer_columns=check_all_characters_present(df,prev_transfer_codes)
next_transfer_columns=check_all_characters_present(df,next_transfer_codes)
prev_transfer_columns,next_transfer_columns

prev_df=df.loc[:,prev_transfer_columns]
next_df=df.loc[:,next_transfer_columns]
prev_df_list=prev_df.values.tolist()
next_df_list=next_df.values.tolist()


def transfer_route_check(df,prev_df_list,next_df_list):
    # Assuming both lists have the same length
    status=[]
    for i in range(len(prev_df_list)):
        prev_data = prev_df_list[i]
        next_data = next_df_list[i]
        prev_count = sum(1 for j in range(1, len(prev_data)) if not pd.isna(prev_data[j]))
        next_count = sum(1 for j in range(1, len(next_data)) if not pd.isna(next_data[j]))
        if prev_count == prev_data[0] and next_count == next_data[0]:
            status.append(0)            
        else:
            status.append(1)
    return status
status_transfers=transfer_route_check(df,prev_df_list,next_df_list)

df['Status']=status_transfers

# desired_columns = ['elvis_date', 'Final_Usage', 'id']  # Specify the desired column order
desired_columns = [elvis_date[0], 'Final_Usage', 'id']  # Specify the desired column order

# Ensure that all desired columns exist in your DataFrame
missing_columns = [col for col in desired_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"Columns {missing_columns} do not exist in df1.")

# Reorder the columns to make them first
df = df[desired_columns + [col for col in df.columns if col not in desired_columns]]
# df.to_csv("Traditional Transfer Checks.csv",index=False)



# Good Transfer Flags
def split_etc_route_id(value):
    value_list = value.split('_')
    etc_id = '_'.join(value_list[:-1])
    return etc_id

# df['ETC_ROUTE_ID_New']=df['ETC_ROUTE_ID'].apply(split_etc_route_id)
# print('ETC_ROUTE_ID Splitted Successfully')
# df.drop_duplicates(subset=['ETC_ROUTE_ID_New'],inplace=True)

stops_columns_to_check=['stoplat','stoplon','etcrouteid']
stops_columns=check_all_characters_present(detail_df,stops_columns_to_check)

stops_df=detail_df.loc[:,stops_columns]
stops_df_list=stops_df.values.tolist()
rev_stops_df_list = stops_df_list[::-1]

from concurrent.futures import ThreadPoolExecutor
from math import radians, sin, cos, sqrt, atan2
from threading import Lock

# Approximate radius of earth in km
R = 6373.0

def get_distance_between_coordinates(start_lat, start_lng, end_lat, end_lng):
    lat1 = radians(start_lat)
    lon1 = radians(start_lng)
    lat2 = radians(end_lat)
    lon2 = radians(end_lng)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance_km = R * c
    distance_in_miles = distance_km * 0.621371  # Convert km to miles
    return distance_in_miles

# without Lock previous Code

# def calculate_distance_for_pair(args):
#     i, stops_df_list, success_list = args
#     results = []
#     for j in range(len(stops_df_list)):
#         # to generate reverse routes for each and every record remove condition befor and
#         if  str(stops_df_list[i][-1]).split('_')[-1] != str(stops_df_list[j][-1]).split('_')[-1]:
#         # if str(stops_df_list[i][-1]).split('_')[-1] == '00' and str(stops_df_list[i][-1]).split('_')[-1] != str(stops_df_list[j][-1]).split('_')[-1]:
#             if str(stops_df_list[i][-1]).split('_')[-2] != str(stops_df_list[j][-1]).split('_')[-2] and f'{stops_df_list[i][-1]} to {stops_df_list[j][-1]}' not in success_list:
#                 distance = get_distance_between_coordinates(
#                     stops_df_list[i][0], stops_df_list[i][1], stops_df_list[j][0], stops_df_list[j][1])
#                 if distance <= 0.25:
#                     success_list.append(f'{stops_df_list[i][-1]} to {stops_df_list[j][-1]}')
#                     splited_list1 = stops_df_list[i][-1].split('_')
#                     splited_value1 = '_'.join(splited_list1[:-1])
#                     splited_list = stops_df_list[j][-1].split('_')
#                     splited_value = '_'.join(splited_list[:-1])
#                     result = f'{splited_value1}>>{splited_value}\n'
#                     results.append(result)
#     return results

# def calculate_and_print_distance(stops_df_list):
#     results = []  # Initialize a list to store the results
#     success_list = []

#     # Create a list of tasks
#     tasks = [(i, stops_df_list, success_list) for i in range(len(stops_df_list))]

#     # Use ThreadPoolExecutor to run tasks in parallel
#     with ThreadPoolExecutor() as executor:
#         thread_results = list(executor.map(calculate_distance_for_pair, tasks))

#     # Flatten the results
#     for res in thread_results:
#         results.extend(res)

#     return results


# with Lock updated Code

def calculate_distance_for_pair(args):
    i, stops_df_list, success_set, lock = args
    results = []
    for j in range(len(stops_df_list)):
        if str(stops_df_list[i][-1]).split('_')[-1] == '00' and str(stops_df_list[i][-1]).split('_')[-1] != str(stops_df_list[j][-1]).split('_')[-1]:
            if str(stops_df_list[i][-1]).split('_')[-2] != str(stops_df_list[j][-1]).split('_')[-2]:
                route_pair = f'{stops_df_list[i][-1]} to {stops_df_list[j][-1]}'
                with lock:
                    if route_pair not in success_set:
                        distance = get_distance_between_coordinates(
                            stops_df_list[i][0], stops_df_list[i][1], stops_df_list[j][0], stops_df_list[j][1])
                        if distance <= 0.25:
                            success_set.add(route_pair)
                            splited_list1 = stops_df_list[i][-1].split('_')
                            splited_value1 = '_'.join(splited_list1[:-1])
                            splited_list = stops_df_list[j][-1].split('_')
                            splited_value = '_'.join(splited_list[:-1])
                            result = f'{splited_value1}>>{splited_value}\n'
                            results.append(result)
    return results

def calculate_and_print_distance(stops_df_list, num_threads=None):
    results = []  # Initialize a list to store the results
    success_set = set()
    lock = Lock()

    # Create a list of tasks
    tasks = [(i, stops_df_list, success_set, lock) for i in range(len(stops_df_list))]

    # Use ThreadPoolExecutor to run tasks in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        thread_results = list(executor.map(calculate_distance_for_pair, tasks))

    # Flatten the results
    for res in thread_results:
        results.extend(res)

    return results




print("Calculating Distances...................")
print("........................................")
print("........................................")
print("........................................")
print("........................................")

file_name = f'{file_first_name}_distances_success.txt'

# Check if the file exists
if os.path.exists(file_name):
    print(f"File '{file_name}' exists. Reading results from the file...")
    
    # Read the file contents
    with open(file_name, 'r') as file:
        results = file.read()

else:
    results = calculate_and_print_distance(stops_df_list)

    print(".....................Distance Calculated")
    # Now results is an iterator of strings. 
    # We'll join these strings together with an empty separator to get the final text.
    final_text = ''.join(results)

    # Write the distances to a text file
    with open(f'{file_first_name}_distances_success.txt', 'w') as file:
        file.write(final_text)

    # print("#####################################################################")
    print(f'File: {file_first_name}_distances_success.txt Created SuccessFully')
    # print("#####################################################################")

# Good Transfer Combo Logic Starts Here
prev_trip_codes_checks=['tripfirstroutecode','tripsecondroutecode','tripthirdroutecode','tripfourthroutecode']
route_survey_checks=['routesurveyedcode']
next_trip_codes_checks=['tripnextroutecode','tripafterroutecode','trip3rdroutecode','triplast4thrtecode']
prev_trip_codes_columns=check_all_characters_present(df,prev_trip_codes_checks)
route_survey_column=check_all_characters_present(df,route_survey_checks)
next_trip_codes_columns=check_all_characters_present(df,next_trip_codes_checks)
transfer_list_columns=[*prev_trip_codes_columns,*route_survey_column,*next_trip_codes_columns]
transfer_list_columns


def process_route_surveyed_code(value):
    splited_list = str(value).split('_')  # Note the [0] to access the string in the inner list
    splited_value = '_'.join(splited_list[:-1])
    return splited_value

# To split/remove _00/_01 from RouteSurveyCode Column
route_survey_values = df[route_survey_column].values.tolist()

route_survey_splited_values=[]
for i in range(0,len(route_survey_values)):
    for value in route_survey_values[i]:
        route_survey_splited_values.append(process_route_surveyed_code(value))

# Set the values without _00/_01 to the Original Route Survey Column
df[route_survey_column[0]]=route_survey_splited_values

# create 'transfers_list' Logic Here 
good_transfer_df=df[transfer_list_columns]
good_transfer_values=good_transfer_df.values.tolist()
good_transfer_values
result_list = []
for values in good_transfer_values:
    non_na_values = [str(value) for value in values if not pd.isna(value)]
    result = '>>'.join(non_na_values)
    result_list.append(result)

df['transfers_list']=result_list

prev_trip_codes_checks=['id','tripfirstroutecode','tripsecondroutecode','tripthirdroutecode','tripfourthroutecode']
route_survey_checks=['routesurveyedcode']
next_trip_codes_checks=['tripnextroutecode','tripafterroutecode','trip3rdroutecode','triplast4thrtecode','transferslist']
# next_trip_codes_checks=['tripnextroutecode','tripafterroutecode','trip3rdroutecode','triplast4thrtecode']
final_reviewer_column_checks=['finalreviewer']
final_reviewer_column=check_all_characters_present(df,final_reviewer_column_checks)


prev_trip_codes_columns=check_all_characters_present(df,prev_trip_codes_checks)
route_survey_column=check_all_characters_present(df,route_survey_checks)
next_trip_codes_columns=check_all_characters_present(df,next_trip_codes_checks)
transfers_new_columns=[*prev_trip_codes_columns,*route_survey_column,*next_trip_codes_columns,*final_reviewer_column]
transfers_new_columns

df1=df[transfers_new_columns]

df1['Duplicate Transfers']=None

# Add Transfer1 to Transfer8 and Check1.GoodTransfer to Check8.GoodTransfer columns in DataFrame
for i in range(1, 9):
    df1[f'Transfer{i}'] = None    
    df1[f'Check{i}.GoodTransfer'] = 0

# Good Transfer Values added based on condition
for index, row in df1.iterrows():
    splited_list = row['transfers_list'].split('>>')
    for i in range(len(splited_list)):
        duplicates = [x for x in splited_list if splited_list.count(x) > 1]
        if duplicates:
            df1.at[index,'Duplicate Transfers']=1
        else:
            df1.at[index,'Duplicate Transfers']=0
    
        if i + 1 < len(splited_list):
            item_to_find = f"{splited_list[i]}>>{splited_list[i + 1]}"
            item_to_check = f"{splited_list[i]}>>{splited_list[i + 1]}"+'\n'

            if '-oth-' in splited_list:
                # Handle -oth- case
                # Set the relevant columns as needed
                df1.at[index, f"Check{i + 1}.GoodTransfer"] = 0
                df1.at[index, f'Transfer{i + 1}'] = item_to_find
            elif item_to_check in results:
                df1.at[index,f"Check{i + 1}.GoodTransfer"] = 0
                df1.at[index,f'Transfer{i + 1}'] = item_to_find
            else:
                df1.at[index,f"Check{i + 1}.GoodTransfer"] = 1
                df1.at[index,f'Transfer{i + 1}'] = item_to_find
        else:
            df1.at[index,f"Check{i + 1}.GoodTransfer"] = 0
            df1.at[index,f'Transfer{i + 1}'] = f"{splited_list[i]}"

df1['real flags']=df['Status']
df1['Checkall.GoodTransfer'] = np.where(df1[['Check1.GoodTransfer', 'Check2.GoodTransfer', 'Check3.GoodTransfer', 'Check4.GoodTransfer', 'Check5.GoodTransfer', 'Check6.GoodTransfer', 'Check7.GoodTransfer', 'Check8.GoodTransfer']].any(axis=1), 1, 0)
condition = ((df1['Checkall.GoodTransfer'] == 1) | (df1['real flags'] == 1))
# condition = ((df1['Checkall.GoodTransfer'] == 1))
df1 = df1[condition]


# Your agency list
agency_list = ["MDT_1_999", 'TRI_1_TR', 'PLM_1_999', 'BRI_1_B1']

# Check if any value in agency_list is present in any cell of a row and drop those rows
df1 = df1[~df1.apply(lambda row: any(val in agency_list for val in row), axis=1)]
df1.drop_duplicates(subset='id', keep='first', inplace=True)

# df1.to_csv(f"{file_first_name}_Traditional_Transfer_Flags(v1).csv",index=False)
df1.to_csv(f"reviewtool_{today_date}_{project_name}_TraditionalTransferFlags.csv",index=False)
print("#####################################################################")
print(f'File: {file_first_name}_Good_Transfer_Combo.csv Created SuccessFully')
print("#####################################################################")
