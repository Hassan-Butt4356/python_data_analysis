import pandas as pd
import numpy as np
import random
import copy
import math
from datetime import date
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# KINGElvis FileName
file_name="VTA_CA_OB_KINGElvis.xlsx"

if file_name.split('_')[0].isdigit():
    file_first_name=file_name.split('_')[0]+'_'+file_name.split('_')[1]
else:
    file_first_name=file_name.split('_')[0]

# in some Compeletion Report LSNAMECODE is splited in some it is not so have to check that
def edit_ls_code_column(x):
    value=x.split('_')
    if len(value)>3:
        route_value="_".join(value[:-1])
    else:
        route_value="_".join(value)
    return route_value


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

# for generated file version
version=2
project_name='STL'
today_date = date.today()
today_date=''.join(str(today_date).split('-'))

# ke_df=pd.read_excel(file_name,sheet_name='Elvis_Review')
# detail_df_stops=pd.read_excel('details_vta_CA_od_excel.xlsx',sheet_name='STOPS')
# detail_df_xfers=pd.read_excel('details_vta_CA_od_excel.xlsx',sheet_name='XFERS')

# wkend_overall_df=pd.read_excel('VTA_CA_CR.xlsx',sheet_name='WkEND-Overall')
# # wkend_overall_df['LS_NAME_CODE']=wkend_overall_df['LS_NAME_CODE'].apply(edit_ls_code_column)
# wkend_route_df=pd.read_excel('VTA_CA_CR.xlsx',sheet_name='WkEND-RouteTotal')
# df=pd.read_csv("reviewtool_20241223_VTA_ROUTE_DIRECTION_CHECk.csv")

# # if we have generated route_direction_database file using route_direction_refator_database.py file then have to replace and rename the columns
# df.drop(columns=['ROUTE_SURVEYEDCode','ROUTE_SURVEYED'],inplace=True)
# df.rename(columns={'ROUTE_SURVEYEDCode_New':'ROUTE_SURVEYEDCode','ROUTE_SURVEYED_NEW':'ROUTE_SURVEYED'},inplace=True) 

# wkday_overall_df=pd.read_excel('VTA_CA_CR.xlsx',sheet_name='WkDAY-Overall')
# # wkday_overall_df['LS_NAME_CODE']=wkday_overall_df['LS_NAME_CODE'].apply(edit_ls_code_column)
# wkday_route_df=pd.read_excel('VTA_CA_CR.xlsx',sheet_name='WkDAY-RouteTotal')


detail_df_stops=pd.read_excel('details_saint_louis_MO_od_excel.xlsx',sheet_name='STOPS')
detail_df_xfers=pd.read_excel('details_saint_louis_MO_od_excel.xlsx',sheet_name='XFERS')

wkend_overall_df=pd.read_excel('STL_MO_CR.xlsx',sheet_name='WkEND-Overall')
# wkend_overall_df['LS_NAME_CODE']=wkend_overall_df['LS_NAME_CODE'].apply(edit_ls_code_column)
wkend_route_df=pd.read_excel('STL_MO_CR.xlsx',sheet_name='WkEND-RouteTotal')
df=pd.read_csv("reviewtool_20250410_STL_ROUTE_DIRECTION_CHECk.csv")

route_surveyed_column_check=['routesurveyed']
route_surveyed_code_column_check=['routesurveyedcode']
route_surveyed_code_column=check_all_characters_present(df,route_surveyed_code_column_check)
route_surveyed_column=check_all_characters_present(df,route_surveyed_column_check)

# if we have generated route_direction_database file using route_direction_refator_database.py file then have to replace and rename the columns
df.drop(columns=[route_surveyed_code_column[0],route_surveyed_column[0]],inplace=True)
df.rename(columns={'ROUTE_SURVEYEDCode_New':'ROUTE_SURVEYEDCode','ROUTE_SURVEYED_NEW':'ROUTE_SURVEYED'},inplace=True) 

wkday_overall_df=pd.read_excel('STL_MO_CR.xlsx',sheet_name='WkDAY-Overall')
# wkday_overall_df['LS_NAME_CODE']=wkday_overall_df['LS_NAME_CODE'].apply(edit_ls_code_column)
wkday_route_df=pd.read_excel('STL_MO_CR.xlsx',sheet_name='WkDAY-RouteTotal')

df['ROUTE_SURVEYEDCode_Splited']=df['ROUTE_SURVEYEDCode'].apply(lambda x:('_').join(str(x).split('_')[:-1]) )


# ke_df=ke_df[ke_df['INTERV_INIT']!='999']
# ke_df=ke_df[ke_df['INTERV_INIT']!=999]
# ke_df=ke_df[ke_df['1st Cleaner']!='No 5 MIN']
# ke_df=ke_df[ke_df['1st Cleaner']!='Test']
# ke_df=ke_df[ke_df['1st Cleaner']!='Test/No 5 MIN']
# ke_df=ke_df[ke_df['Final_Usage'].str.lower()=='use']



# Getting Data from Database where the Final Usage is Use in KINGELVIS  
# df=pd.merge(df,ke_df['id'],on='id',how='inner')
df=df[df['INTERV_INIT']!='999']
df=df[df['INTERV_INIT']!=999]
df.drop_duplicates(subset='id',inplace=True)

elvis_status_check=['elvisstatus']
elvis_status=check_all_characters_present(df,elvis_status_check)
df=df[df[elvis_status[0]].str.lower()!='delete']

date_columns_check=['completed','datestarted']
date_columns=check_all_characters_present(df,date_columns_check)

def determine_date(row):
    if not pd.isnull(row[date_columns[0]]):
        return row[date_columns[0]]
    elif not pd.isnull(row[date_columns[1]]):
        return row[date_columns[1]]
    else:
        return pd.NaT

df['Date'] = df.apply(determine_date, axis=1)

# def get_day_name(x):
#     date_object = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
#     day_name = date_object.strftime('%A')
#     return day_name

# def get_day_name(x):
#     # Adjust the format to match your date string
#     date_object = datetime.strptime(x, '%d/%m/%Y %H:%M')
#     day_name = date_object.strftime('%A')
#     return day_name

def get_day_name(x):
    formats_to_check = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M']
    
    for format_str in formats_to_check:
        try:
            date_object = datetime.strptime(x, format_str)
            day_name = date_object.strftime('%A')
            return day_name
        except ValueError:
            continue

df['Day']=df['Date'].apply(get_day_name)


# df['LAST_SURVEY_DATE'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M')
# latest_date = df['LAST_SURVEY_DATE'].max()
# latest_date_df = pd.DataFrame({'Latest_Survey_Date': [latest_date]})

df['LAST_SURVEY_DATE'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
latest_date = df['LAST_SURVEY_DATE'].max()
latest_date_df = pd.DataFrame({'Latest_Survey_Date': [latest_date]})


weekend_df=df[df['Day'].isin(['Saturday','Sunday'])]

weekday_df=df[~(df['Day'].isin(['Saturday','Sunday']))]


# df.to_csv('Day Time SantaClarita.csv',index=False)

# exit()
#to get the TIMEON column
time_column_check=['timeoncode']
time_period_column_check=['timeon']
time_column=check_all_characters_present(df,time_column_check)
time_period_column=check_all_characters_present(df,time_period_column_check)
route_survey_column_check=['routesurveyedcode']
route_survey_column=check_all_characters_present(df,route_survey_column_check)
stopon_clntid_column_check=['stoponclntid']
stopon_clntid_column=check_all_characters_present(df,stopon_clntid_column_check)
stopoff_clntid_column_check=['stopoffclntid']
stopoff_clntid_column=check_all_characters_present(df,stopoff_clntid_column_check)


# df[['id','Day',route_survey_column[0]]].to_csv('Checking Day Names.csv',index=False)


#values to compare AM, MIDDAY, PM and Evening values
# am_values=['AM1','AM2','AM3','MID1','MID2']
# am_values=[1,2,3,4,5]
# midday_values=['MID3','MID4','MID5','MID6','MID7','PM1']
# midday_values=[6,7,8,9,10,11]
# pm_values=['PM2','PM3','PM4','PM5']
# pm_values=[12,13,14]
# evening_values=['PM6','PM7','PM8','PM9']
# evening_values=[15,16,17,18]

wkend_overall_df.dropna(subset=['LS_NAME_CODE'],inplace=True)
wkday_overall_df.dropna(subset=['LS_NAME_CODE'],inplace=True)


def create_time_value_df_with_display(df):
    """
    Create a time-value DataFrame summarizing counts and time ranges.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing the time values.
        time_column (str): Name of the column in the input DataFrame containing the time values.

    Returns:
        pd.DataFrame: Processed DataFrame with counts, time ranges, and display text.
    """
    # Define time value groups

    am_values = ['AM1','AM2','AM3', 'AM4']
    midday_values = ['MID1','MID2', 'MID3', 'MID4', 'MID5']
    pm_values = ['PM1','PM2','PM3','PM4','PM5']
    evening_values = ['EVE1','EVE2','EVE3','EVE4']


    # Mapping time groups to corresponding columns
    time_group_mapping = {
        1: am_values,
        2: midday_values,
        3: pm_values,
        4: evening_values
    }


    time_mapping = {
        'AM1': 'Before 6:00 am',
        'AM2': '6:00 am - 7:00 am',
        'AM3': '7:00 am - 8:00 am',
        'AM4': '8:00 am - 9:00 am',
        'MID1': '9:00 am - 10:00 am',
        'MID2': '10:00 am - 11:00 am',
        'MID3': '11:00 am - 12:00 pm',
        'MID4': '12:00 pm - 1:00 pm',
        'MID5': '1:00 pm - 2:00 pm',
        'PM1': '2:00 pm - 3:00 pm',
        'PM2': '3:00 pm - 4:00 pm',
        'PM3': '4:00 pm - 5:00 pm',
        'PM4': '5:00 pm - 6:00 pm',
        'PM5': '6:00 pm - 7:00 pm',
        'EVE1': '7:00 pm - 8:00 pm',
        'EVE2': '8:00 pm - 9:00 pm',
        'EVE3': '9:00 pm - 10:00 pm',
        'EVE4': 'After 10:00 pm'
    }


    # Initialize the new DataFrame
    new_df = pd.DataFrame(columns=["Original Text", 1, 2, 3, 4])

    # Populate the DataFrame with counts
    for col, values in time_group_mapping.items():
        for value in values:
            count = df[df[time_column[0]] == value].shape[0]
            row = {"Original Text": value}

            # Initialize all columns to 0
            for c in range(1,5):
                row[c] = 0

            # Update the corresponding column with the count
            row[col] = count
            new_df = pd.concat([new_df, pd.DataFrame([row])], ignore_index=True)

    # Map time values to time ranges
    new_df['Time Range'] = new_df['Original Text'].map(time_mapping)

    # Drop rows with missing time ranges
    new_df.dropna(subset=['Time Range'], inplace=True)

    # Add a display text column with sequential numbering
    new_df['Display_Text'] = range(1, len(new_df) + 1)

    return new_df

wkend_time_value_df=create_time_value_df_with_display(weekend_df)
wkday_time_value_df=create_time_value_df_with_display(weekday_df)


# To create Route_SurveyedCode Direction wise comparison in terms of time values
def create_route_direction_level_df(overalldf, df):

    am_values = ['AM1','AM2','AM3', 'AM4']
    midday_values = ['MID1','MID2', 'MID3', 'MID4', 'MID5']
    pm_values = ['PM1','PM2','PM3','PM4','PM5']
    evening_values = ['EVE1','EVE2','EVE3','EVE4']

    am_column = [1]
    midday_colum = [2]
    pm_column = [3]
    evening_column = [4]

    def convert_string_to_integer(x):
        try:
            return float(x)
        except (ValueError, TypeError):
            return 0

    new_df = pd.DataFrame()
    new_df['ROUTE_SURVEYEDCode'] = overalldf['LS_NAME_CODE']
    
    # Create columns with consistent naming

    new_df['CR_AM_Peak'] = pd.to_numeric(overalldf[am_column[0]], errors='coerce').fillna(0).apply(math.ceil)
    new_df['CR_Midday'] = pd.to_numeric(overalldf[midday_colum[0]], errors='coerce').fillna(0).apply(math.ceil)
    new_df['CR_PM'] = pd.to_numeric(overalldf[pm_column[0]], errors='coerce').fillna(0).apply(math.ceil)
    new_df['CR_Evening'] = pd.to_numeric(overalldf[evening_column[0]], errors='coerce').fillna(0).apply(math.ceil)

    new_df[['CR_AM_Peak','CR_Midday','CR_PM','CR_Evening']] =new_df[['CR_AM_Peak','CR_Midday','CR_PM','CR_Evening']].applymap(convert_string_to_integer)
    new_df.fillna(0, inplace=True)

    # Define time_column (was missing in original code)
#     time_column = ['your_time_column_name']  # Replace with actual column name from df

    for index, row in new_df.iterrows():
        route_code = row['ROUTE_SURVEYEDCode']

        def get_counts_and_ids(time_values):
            subset_df = df[(df['ROUTE_SURVEYEDCode'] == route_code) & (df[time_column[0]].isin(time_values))]
            subset_df = subset_df.drop_duplicates(subset='id')
            count = subset_df.shape[0]
            ids = subset_df['id'].values
            return count, ids
    
        am_value, am_value_ids = get_counts_and_ids(am_values)
        midday_value, midday_value_ids = get_counts_and_ids(midday_values)
        pm_value, pm_value_ids = get_counts_and_ids(pm_values)
        evening_value, evening_value_ids = get_counts_and_ids(evening_values)
        
        # Use consistent column names (matching the creation above)
        new_df.loc[index, 'CR_Total'] = (row['CR_AM_Peak'] + row['CR_Midday'] + 
                                        row['CR_PM'] + row['CR_Evening'])
        new_df.loc[index, 'CR_AM_Peak'] = row['CR_AM_Peak']

        new_df.loc[index, 'DB_AM_Peak'] = am_value
        new_df.loc[index, 'DB_Midday'] = midday_value
        new_df.loc[index, 'DB_PM'] = pm_value
        new_df.loc[index, 'DB_Evening'] = evening_value
        new_df.loc[index, 'DB_Total'] = (evening_value + am_value + midday_value + pm_value )

        route_code_level_df=pd.DataFrame()

        unique_routes=new_df['ROUTE_SURVEYEDCode'].unique()

        route_code_level_df['ROUTE_SURVEYEDCode']=unique_routes

        # weekend_df.rename(columns={'ROUTE_TOTAL':'CR_Overall_Goal','SURVEY_ROUTE_CODE':'ROUTE_SURVEYEDCode','LS_NAME_CODE':'ROUTE_SURVEYEDCode'},inplace=True)

        for index, row in new_df.iterrows():
            # pre_early_am_peak_diff=row['CR_PRE_Early_AM']-row['DB_PRE_Early_AM_Peak']

            am_peak_diff=row['CR_AM_Peak']-row['DB_AM_Peak']
            midday_diff=row['CR_Midday']-row['DB_Midday']    
            pm_diff=row['CR_PM']-row['DB_PM']
            evening_diff=row['CR_Evening']-row['DB_Evening']
            total_diff=row['CR_Total']-row['DB_Total']
            new_df.loc[index, 'AM_DIFFERENCE'] = math.ceil(max(0, am_peak_diff))
            new_df.loc[index, 'Midday_DIFFERENCE'] = math.ceil(max(0, midday_diff))
            new_df.loc[index, 'PM_DIFFERENCE'] = math.ceil(max(0, pm_diff))
            new_df.loc[index, 'Evening_DIFFERENCE'] = math.ceil(max(0, evening_diff))
            new_df.loc[index, 'Total_DIFFERENCE'] =math.ceil(max(0, am_peak_diff))+math.ceil(max(0, midday_diff))+math.ceil(max(0, pm_diff))+math.ceil(max(0, evening_diff))
    return new_df

# Usage
wkend_route_direction_df = create_route_direction_level_df(wkend_overall_df, weekend_df)
wkday_route_direction_df = create_route_direction_level_df(wkday_overall_df, weekday_df)



def create_route_level_df(overall_df, route_df, df):
    am_values = ['AM1','AM2','AM3', 'AM4']
    midday_values = ['MID1','MID2', 'MID3', 'MID4', 'MID5']
    pm_values = ['PM1','PM2','PM3','PM4','PM5']
    evening_values = ['EVE1','EVE2','EVE3','EVE4']

    am_column = [1]
    midday_colum = [2]
    pm_column = [3]
    evening_column = [4]

    def convert_string_to_integer(x):
        try:
            return float(x)
        except (ValueError, TypeError):
            return 0

    # Creating new dataframe
    new_df = pd.DataFrame()
    new_df['ROUTE_SURVEYEDCode'] = overall_df['LS_NAME_CODE']
    
    # Create columns with consistent naming
    new_df['CR_AM_Peak'] = pd.to_numeric(overall_df[am_column[0]], errors='coerce').fillna(0).apply(math.ceil)
    new_df['CR_Midday'] = pd.to_numeric(overall_df[midday_colum[0]], errors='coerce').fillna(0).apply(math.ceil)
    new_df['CR_PM'] = pd.to_numeric(overall_df[pm_column[0]], errors='coerce').fillna(0).apply(math.ceil)
    new_df['CR_Evening'] = pd.to_numeric(overall_df[evening_column[0]], errors='coerce').fillna(0).apply(math.ceil)

    
    new_df[['CR_AM_Peak','CR_Midday','CR_PM','CR_Evening']] =new_df[['CR_AM_Peak','CR_Midday','CR_PM','CR_Evening']].applymap(convert_string_to_integer)
    new_df.fillna(0, inplace=True)

    # Define time_column - replace with your actual column name
#     time_column = ['Time_Period']  # Adjust this to match your df column name containing AM1, AM2, etc.

    # Populate DB columns
    for index, row in new_df.iterrows():
        route_code = row['ROUTE_SURVEYEDCode']

        def get_counts_and_ids(time_values):
            subset_df = df[(df['ROUTE_SURVEYEDCode'] == route_code) & (df[time_column[0]].isin(time_values))]
            subset_df = subset_df.drop_duplicates(subset='id')
            count = subset_df.shape[0]
            ids = subset_df['id'].values
            return count, ids
        
        am_value, _ = get_counts_and_ids(am_values)
        midday_value, _ = get_counts_and_ids(midday_values)
        pm_value, _ = get_counts_and_ids(pm_values)
        evening_value, _ = get_counts_and_ids(evening_values)
        
        # Use consistent column names
        new_df.loc[index, 'CR_Total'] = ( row['CR_AM_Peak'] + row['CR_Midday'] +row['CR_PM'] + row['CR_Evening'])
        # new_df.loc[index, 'CR_AM_Peak'] = row['CR_AM_Peak']


        new_df.loc[index, 'DB_AM_Peak'] = am_value
        new_df.loc[index, 'DB_Midday'] = midday_value
        new_df.loc[index, 'DB_PM'] = pm_value
        new_df.loc[index, 'DB_Evening'] = evening_value
        new_df.loc[index, 'DB_Total'] = (evening_value + am_value + midday_value + pm_value)

    # Route Level Comparison
    new_df['ROUTE_SURVEYEDCode_Splited'] = new_df['ROUTE_SURVEYEDCode'].apply(lambda x: '_'.join(x.split('_')[:-1]))
    new_df.to_csv('W')
    # Create route_level_df
    route_level_df = pd.DataFrame()
    unique_routes = new_df['ROUTE_SURVEYEDCode_Splited'].unique()
    route_level_df['ROUTE_SURVEYEDCode'] = unique_routes

    route_df.rename(columns={'ROUTE_TOTAL':'CR_Overall_Goal','SURVEY_ROUTE_CODE':'ROUTE_SURVEYEDCode','LS_NAME_CODE':'ROUTE_SURVEYEDCode'}, inplace=True)
    route_df.dropna(subset=['ROUTE_SURVEYEDCode'], inplace=True)
    route_level_df = pd.merge(route_level_df, route_df[['ROUTE_SURVEYEDCode','CR_Overall_Goal']], on='ROUTE_SURVEYEDCode')

    # Populate route-level sums
    for index, row in route_level_df.iterrows():
        subset_df = new_df[new_df['ROUTE_SURVEYEDCode_Splited'] == row['ROUTE_SURVEYEDCode']]
        sum_per_route_cr = subset_df[['CR_AM_Peak', 'CR_Midday', 'CR_PM', 'CR_Evening', 'CR_Total']].sum()
        sum_per_route_db = subset_df[['DB_AM_Peak', 'DB_Midday', 'DB_PM', 'DB_Evening', 'DB_Total']].sum()
        

        route_level_df.loc[index,'CR_AM_Peak'] = sum_per_route_cr['CR_AM_Peak']
        route_level_df.loc[index,'CR_Midday'] = sum_per_route_cr['CR_Midday']
        route_level_df.loc[index,'CR_PM'] = sum_per_route_cr['CR_PM']
        route_level_df.loc[index,'CR_Evening'] = sum_per_route_cr['CR_Evening']
        route_level_df.loc[index,'CR_Total'] = sum_per_route_cr['CR_Total']
        

        route_level_df.loc[index,'DB_AM_Peak'] = sum_per_route_db['DB_AM_Peak']
        route_level_df.loc[index,'DB_Midday'] = sum_per_route_db['DB_Midday']
        route_level_df.loc[index,'DB_PM'] = sum_per_route_db['DB_PM']
        route_level_df.loc[index,'DB_Evening'] = sum_per_route_db['DB_Evening']
        route_level_df.loc[index,'DB_Total'] = sum_per_route_db['DB_Total']

    # Calculate differences
    for index, row in route_level_df.iterrows():

        am_peak_diff = row['CR_AM_Peak'] - row['DB_AM_Peak']
        midday_diff = row['CR_Midday'] - row['DB_Midday']
        pm_diff = row['CR_PM'] - row['DB_PM']
        evening_diff = row['CR_Evening'] - row['DB_Evening']
        total_diff = row['CR_Total'] - row['DB_Total']
        overall_difference = row['CR_Overall_Goal'] - row['DB_Total']
        
        route_level_df.loc[index, 'AM_DIFFERENCE'] = math.ceil(max(0, am_peak_diff))
        route_level_df.loc[index, 'Midday_DIFFERENCE'] = math.ceil(max(0, midday_diff))
        route_level_df.loc[index, 'PM_DIFFERENCE'] = math.ceil(max(0, pm_diff))
        route_level_df.loc[index, 'Evening_DIFFERENCE'] = math.ceil(max(0, evening_diff))
        route_level_df.loc[index, 'Total_DIFFERENCE'] = (math.ceil(max(0, am_peak_diff)) +math.ceil(max(0, midday_diff)) + math.ceil(max(0, pm_diff)) + math.ceil(max(0, evening_diff)))
        route_level_df.loc[index, 'Overall_Goal_DIFFERENCE'] = math.ceil(max(0, overall_difference))

    return route_level_df



weekday_df.dropna(subset=[time_column[0]],inplace=True)
weekday_raw_df=weekday_df[['id','Completed',route_survey_column[0],'ROUTE_SURVEYED',stopon_clntid_column[0],stopoff_clntid_column[0],time_column[0],time_period_column[0],'Day','ELVIS_STATUS']]
weekend_df.dropna(subset=[time_column[0]],inplace=True)
weekend_raw_df=weekend_df[['id','Completed',route_survey_column[0],'ROUTE_SURVEYED',stopon_clntid_column[0],stopoff_clntid_column[0],time_column[0],time_period_column[0],'Day','ELVIS_STATUS']]
weekend_raw_df.rename(columns={stopon_clntid_column[0]:'BOARDING LOCATION',stopoff_clntid_column[0]:'ALIGHTING LOCATION'},inplace=True)
weekday_raw_df.rename(columns={stopon_clntid_column[0]:'BOARDING LOCATION',stopoff_clntid_column[0]:'ALIGHTING LOCATION'},inplace=True)


wkday_route_level =create_route_level_df(wkday_overall_df,wkday_route_df,weekday_df)
wkend_route_level =create_route_level_df(wkend_overall_df,wkend_route_df,weekend_df)
# wkday_route_df.to_csv("CHECk TOTAL_Difference.csv",index=False)
# wkend_route_df.to_csv("WKENDCHECk TOTAL_Difference.csv",index=False)
wkday_comparison_df=copy.deepcopy(wkday_route_level)
wkday_new_route_level_df=copy.deepcopy(wkday_route_level)

wkend_comparison_df=copy.deepcopy(wkend_route_level)
wkend_new_route_level_df=copy.deepcopy(wkend_route_level)

if not wkday_comparison_df.empty:
    for index , row in wkday_comparison_df.iterrows():
        wkday_comparison_df.loc[index,'Total_DIFFERENCE']=math.ceil(max(0,(row['CR_Total']-row['DB_Total'])))
else:
    wkday_comparison_df['Total_DIFFERENCE']=0


if not wkend_comparison_df.empty:
    for index , row in wkend_comparison_df.iterrows():
        wkend_comparison_df.loc[index,'Total_DIFFERENCE']=math.ceil(max(0,(row['CR_Total']-row['DB_Total'])))
else:
    wkend_comparison_df['Total_DIFFERENCE']=0



# wkend_comparison_df.rename(columns={'CR_PRE_Early_AM':'(0) Goal','CR_Early_AM':'(1) Goal','CR_AM_Peak':'(2) Goal','CR_Midday':'(3) Goal','CR_PM_Peak':'(4) Goal','CR_Evening':'(5) Goal',
#          'DB_PRE_Early_AM_Peak':'(0) Collect', 'DB_Early_AM_Peak':'(1) Collect', 'DB_AM_Peak':'(2) Collect',
#        'DB_Midday':'(3) Collect', 'DB_PM_Peak':'(4) Collect', 'DB_Evening':'(5) Collect','PRE_Early_AM_DIFFERENCE':'(0) Remain',
#        'Early_AM_DIFFERENCE':'(1) Remain', 'AM_DIFFERENCE':'(2) Remain', 'Midday_DIFFERENCE':'(3) Remain',
#        'PM_DIFFERENCE':'(4) Remain', 'Evening_DIFFERENCE':'(5) Remain','CR_Overall_Goal':'Route Level Goal','DB_Total':'# of Surveys','Overall_Goal_DIFFERENCE':'Remaining'},inplace=True)

# wkday_comparison_df.rename(columns={'CR_PRE_Early_AM':'(0) Goal','CR_Early_AM':'(1) Goal','CR_AM_Peak':'(2) Goal','CR_Midday':'(3) Goal','CR_PM_Peak':'(4) Goal','CR_Evening':'(5) Goal',
#          'DB_PRE_Early_AM_Peak':'(0) Collect', 'DB_Early_AM_Peak':'(1) Collect', 'DB_AM_Peak':'(2) Collect',
#        'DB_Midday':'(3) Collect', 'DB_PM_Peak':'(4) Collect', 'DB_Evening':'(5) Collect','PRE_Early_AM_DIFFERENCE':'(0) Remain',
#        'Early_AM_DIFFERENCE':'(1) Remain', 'AM_DIFFERENCE':'(2) Remain', 'Midday_DIFFERENCE':'(3) Remain',
#        'PM_DIFFERENCE':'(4) Remain', 'Evening_DIFFERENCE':'(5) Remain','CR_Overall_Goal':'Route Level Goal','DB_Total':'# of Surveys','Overall_Goal_DIFFERENCE':'Remaining'},inplace=True)

# wkday_route_direction_df.rename(columns={'CR_PRE_Early_AM':'(0) Goal','CR_Early_AM':'(1) Goal','CR_AM_Peak':'(2) Goal','CR_Midday':'(3) Goal','CR_PM_Peak':'(4) Goal','CR_Evening':'(5) Goal',
#          'DB_PRE_Early_AM_Peak':'(0) Collect', 'DB_Early_AM_Peak':'(1) Collect', 'DB_AM_Peak':'(2) Collect',
#        'DB_Midday':'(3) Collect', 'DB_PM_Peak':'(4) Collect', 'DB_Evening':'(5) Collect','PRE_Early_AM_DIFFERENCE':'(0) Remain',
#        'Early_AM_DIFFERENCE':'(1) Remain', 'AM_DIFFERENCE':'(2) Remain', 'Midday_DIFFERENCE':'(3) Remain',
#        'PM_DIFFERENCE':'(4) Remain', 'Evening_DIFFERENCE':'(5) Remain'},inplace=True)

# wkend_route_direction_df.rename(columns={'CR_PRE_Early_AM':'(0) Goal','CR_Early_AM':'(1) Goal','CR_AM_Peak':'(2) Goal','CR_Midday':'(3) Goal','CR_PM_Peak':'(4) Goal','CR_Evening':'(5) Goal',
#          'DB_PRE_Early_AM_Peak':'(0) Collect', 'DB_Early_AM_Peak':'(1) Collect', 'DB_AM_Peak':'(2) Collect',
#        'DB_Midday':'(3) Collect', 'DB_PM_Peak':'(4) Collect', 'DB_Evening':'(5) Collect','PRE_Early_AM_DIFFERENCE':'(0) Remain',
#        'Early_AM_DIFFERENCE':'(1) Remain', 'AM_DIFFERENCE':'(2) Remain', 'Midday_DIFFERENCE':'(3) Remain',
#        'PM_DIFFERENCE':'(4) Remain', 'Evening_DIFFERENCE':'(5) Remain'},inplace=True)



wkend_comparison_df.rename(columns={'CR_AM_Peak':'(1) Goal','CR_Midday':'(2) Goal','CR_PM':'(3) Goal','CR_Evening':'(4) Goal',
         'DB_AM_Peak':'(1) Collect',
       'DB_Midday':'(2) Collect', 'DB_PM':'(3) Collect',  'DB_Evening':'(4) Collect', 'AM_DIFFERENCE':'(1) Remain', 'Midday_DIFFERENCE':'(2) Remain',
       'PM_DIFFERENCE':'(3) Remain','Evening_DIFFERENCE':'(4) Remain','CR_Overall_Goal':'Route Level Goal','DB_Total':'# of Surveys','Overall_Goal_DIFFERENCE':'Remaining'},inplace=True)

wkday_comparison_df.rename(columns={'CR_AM_Peak':'(1) Goal','CR_Midday':'(2) Goal','CR_PM':'(3) Goal','CR_Evening':'(4) Goal',
         'DB_AM_Peak':'(1) Collect',
       'DB_Midday':'(2) Collect', 'DB_PM':'(3) Collect',  'DB_Evening':'(4) Collect',  'AM_DIFFERENCE':'(1) Remain', 'Midday_DIFFERENCE':'(2) Remain',
       'PM_DIFFERENCE':'(3) Remain', 'Evening_DIFFERENCE':'(4) Remain','CR_Overall_Goal':'Route Level Goal','DB_Total':'# of Surveys','Overall_Goal_DIFFERENCE':'Remaining'},inplace=True)

wkday_route_direction_df.rename(columns={'CR_AM_Peak':'(1) Goal','CR_Midday':'(2) Goal','CR_PM':'(3) Goal','CR_Evening':'(4) Goal',
         'DB_AM_Peak':'(1) Collect',
       'DB_Midday':'(2) Collect', 'DB_PM':'(3) Collect', 'DB_Evening':'(4) Collect','AM_DIFFERENCE':'(1) Remain', 'Midday_DIFFERENCE':'(2) Remain',
       'PM_DIFFERENCE':'(3) Remain', 'Evening_DIFFERENCE':'(4) Remain','CR_Overall_Goal':'Route Level Goal','DB_Total':'# of Surveys','Overall_Goal_DIFFERENCE':'Remaining'},inplace=True)

wkend_route_direction_df.rename(columns={'CR_AM_Peak':'(1) Goal','CR_Midday':'(2) Goal','CR_PM':'(3) Goal','CR_Evening':'(4) Goal',
         'DB_AM_Peak':'(1) Collect',
       'DB_Midday':'(2) Collect', 'DB_PM':'(3) Collect', 'DB_Evening':'(4) Collect', 'AM_DIFFERENCE':'(1) Remain', 'Midday_DIFFERENCE':'(2) Remain',
       'PM_DIFFERENCE':'(3) Remain', 'Evening_DIFFERENCE':'(4) Remain','CR_Overall_Goal':'Route Level Goal','DB_Total':'# of Surveys','Overall_Goal_DIFFERENCE':'Remaining'},inplace=True)


wkday_comparison_df = wkday_comparison_df.merge(
    detail_df_xfers[['ETC_ROUTE_ID', 'ETC_ROUTE_NAME']],
    left_on='ROUTE_SURVEYEDCode',
    right_on='ETC_ROUTE_ID',
    how='left'
)

# Rename the column as per requirement
wkday_comparison_df.rename(columns={'ETC_ROUTE_NAME': 'ROUTE_SURVEYED'}, inplace=True)
wkday_comparison_df.drop(columns=['ETC_ROUTE_ID'], inplace=True)

wkend_comparison_df = wkend_comparison_df.merge(
    detail_df_xfers[['ETC_ROUTE_ID', 'ETC_ROUTE_NAME']],
    left_on='ROUTE_SURVEYEDCode',
    right_on='ETC_ROUTE_ID',
    how='left'
)

# Rename the column as per requirement
wkend_comparison_df.rename(columns={'ETC_ROUTE_NAME': 'ROUTE_SURVEYED'}, inplace=True)
wkend_comparison_df.drop(columns=['ETC_ROUTE_ID'], inplace=True)

for _,row in wkday_route_direction_df.iterrows():
    route_surveyed=detail_df_stops[detail_df_stops['ETC_ROUTE_ID']==row['ROUTE_SURVEYEDCode']]['ETC_ROUTE_NAME'].iloc[0]
    route_surveyed_ID=detail_df_stops[detail_df_stops['ETC_ROUTE_ID']==row['ROUTE_SURVEYEDCode']]['ETC_ROUTE_ID'].iloc[0]
    wkday_route_direction_df.loc[row.name,'ROUTE_SURVEYED']=route_surveyed  

for _,row in wkend_route_direction_df.iterrows():
    route_surveyed=detail_df_stops[detail_df_stops['ETC_ROUTE_ID']==row['ROUTE_SURVEYEDCode']]['ETC_ROUTE_NAME'].iloc[0]
    route_surveyed_ID=detail_df_stops[detail_df_stops['ETC_ROUTE_ID']==row['ROUTE_SURVEYEDCode']]['ETC_ROUTE_ID'].iloc[0]
    wkend_route_direction_df.loc[row.name,'ROUTE_SURVEYED']=route_surveyed  

# f'{file_first_name} Route Level Comparison(Wkday & WkEnd)(v{version}).xlsx'
with pd.ExcelWriter(f'reviewtool_{today_date}_{project_name}_RouteLevelComparison(Wkday & WkEnd)_Latest_01.xlsx') as writer:
    # wkday_route_direction_df.drop(columns=['CR_Total','Total_DIFFERENCE','DB_Total']).to_excel(writer,sheet_name='WkDAY Route DIR Comparison',index=False)
    # wkend_route_direction_df.drop(columns=['CR_Total','Total_DIFFERENCE','DB_Total']).to_excel(writer,sheet_name='WkEND Route DIR Comparison',index=False)
    
    wkday_route_direction_df.drop(columns=['CR_Total','Total_DIFFERENCE']).to_excel(writer,sheet_name='WkDAY Route DIR Comparison',index=False)
    wkend_route_direction_df.drop(columns=['CR_Total','Total_DIFFERENCE']).to_excel(writer,sheet_name='WkEND Route DIR Comparison',index=False)
    
    weekday_raw_df.to_excel(writer,sheet_name='WkDAY RAW DATA',index=False)
    weekend_raw_df.to_excel(writer,sheet_name='WkEND RAW DATA',index=False)

    wkend_time_value_df.to_excel(writer,sheet_name='WkEND Time Data',index=False)
    wkday_time_value_df.to_excel(writer,sheet_name='WkDAY Time Data',index=False)

    # wkday_comparison_df.drop(columns=['CR_Total','DB_PRE_Early_AM_IDS','DB_Early_AM_IDS','DB_AM_IDS','DB_Midday_IDS','DB_PM_IDS','DB_Evening_IDS','Total_DIFFERENCE']).to_excel(writer,sheet_name='WkDAY Route Comparison',index=False)
    # wkend_comparison_df.drop(columns=['CR_Total','DB_PRE_Early_AM_IDS','DB_Early_AM_IDS','DB_AM_IDS','DB_Midday_IDS','DB_PM_IDS','DB_Evening_IDS','Total_DIFFERENCE']).to_excel(writer,sheet_name='WkEND Route Comparison',index=False)
    
    wkday_comparison_df.drop(columns=['CR_Total','Total_DIFFERENCE']).to_excel(writer,sheet_name='WkDAY Route Comparison',index=False)
    wkend_comparison_df.drop(columns=['CR_Total','Total_DIFFERENCE']).to_excel(writer,sheet_name='WkEND Route Comparison',index=False)

    latest_date_df.to_excel(writer, index=False, sheet_name='LAST SURVEY DATE')

    # wkday_all_type_df[['id',route_survey_column[0],route_survey_name_column[0],'Type','COMPLETED By']].to_excel(writer,sheet_name='Reverse Routes',index=False)
    # wkday_reverse_df_filtered[['id', route_survey_column[0], route_survey_name_column[0], 'Type', 'COMPLETED By']].to_excel(writer, sheet_name='Reverse Routes WkDAY', index=False)
    # wkend_reverse_df_filtered[['id', route_survey_column[0], route_survey_name_column[0], 'Type', 'COMPLETED By']].to_excel(writer, sheet_name='Reverse Routes WkEND', index=False)
    
    # wkday_reverse_df_filtered[['id', route_survey_column[0], route_survey_name_column[0], 'Type', 'COMPLETED By','Generated Trips']].to_excel(writer, sheet_name='Reverse Routes WkDAY', index=False)
    # wkend_reverse_df_filtered[['id', route_survey_column[0], route_survey_name_column[0], 'Type', 'COMPLETED By','Generated Trips']].to_excel(writer, sheet_name='Reverse Routes WkEND', index=False)
print("Files Generated SuccessFully")