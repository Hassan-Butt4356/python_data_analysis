import pandas as pd
import numpy as np
import random
import copy
import math
import warnings

warnings.filterwarnings('ignore')

# To read all required Files
# cota files
# cr_df=pd.read_excel('COTA_CR_Headers.xlsx',sheet_name='WkDAY-Overall')
# df=pd.read_csv("elviscota2023obweekday_export_odbc(V3).csv")
# ke_df=pd.read_excel("COTA_KINGElvis (4).xlsx",sheet_name='Elvis_Review')
# sample_df=pd.read_excel('2023 COTA OD Sampling Plan 20231019.xlsx',sheet_name='Sheet1',header=3)

# this is for time of day values
cr_df=pd.read_excel('project_CR_Santa Clarita (3).xlsx',sheet_name='WkDAY-Overall')
# this is for overall goal values
wkday_route_df=pd.read_excel('project_CR_Santa Clarita (3).xlsx',sheet_name='WkDAY-RouteTotal')
df=pd.read_csv("elvissantaclarita2023obweekday_export_odbc(v1).csv")
ke_df=pd.read_excel("SantaClarita_KINGElvis.xlsx",sheet_name='Elvis_Review')


# cr_df=pd.read_csv('SantaClarita WkDAY-Overall.csv')

# reno files
# cr_df=pd.read_excel('project_CR_RENO (2).xlsx',sheet_name='WkDAY-Overall')
# df=pd.read_csv("elvisreno_od2023_weekday_export_odbc(new_001).csv")
# ke_df=pd.read_excel("RENO_KINGElvis (5).xlsx",sheet_name='Elvis_Review')

#  Removing the Test Records and Getting only that data where Final Usage is Use from KINGElvis file
ke_df=ke_df[ke_df['INTERV_INIT']!='999']
ke_df=ke_df[ke_df['INTERV_INIT']!=999]
ke_df=ke_df[ke_df['1st Cleaner']!='Test/No 5 MIN']
ke_df=ke_df[ke_df['Final_Usage'].str.lower()=='use']

# Getting Data from Database where the Final Usage is Use in KINGELVIS  
df=pd.merge(df,ke_df['id'],on='id',how='inner')
df.drop_duplicates(subset='id',inplace=True)

# print(df['ROUTE_SURVEYEDCode'].unique())
# print(len(df['ROUTE_SURVEYEDCode'].unique()))
# exit()

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


#to get the TIMEON column
time_column_check=['timeoncode']
time_column=check_all_characters_present(df,time_column_check)

# to get ROUTE_SURVEYEDCode column from database File
route_survey_column_check=['routesurveyedcode']
route_survey_column=check_all_characters_present(df,route_survey_column_check)


#values to compare AM, MIDDAY, PM and Evening values
am_values=['AM1','AM2','AM3','AM4']
midday_values=['MID1','MID2','MID3','MID4','MID5']
pm_values=['MID6','PM1','PM2','PM3']
evening_values=['PM4','PM5','PM6','PM7']

cr_df.dropna(subset=['LS_NAME_CODE'],inplace=True)

# reno
am_column_check=['ampeak']
pm_column_check=['pmpeak']
midday_column_check=['midday']
evening_column_check=['evening']
overall_goal_column_check=['totalsurveys']

# cota
# am_column_check=['am']
# pm_column_check=['pm']
# midday_column_check=['midday']
# evening_column_check=['eve']

am_column=check_all_characters_present(cr_df,am_column_check)
pm_column=check_all_characters_present(cr_df,pm_column_check)
midday_colum=check_all_characters_present(cr_df,midday_column_check)
evening_column=check_all_characters_present(cr_df,evening_column_check)
# overall_goal_column=check_all_characters_present(cr_df,overall_goal_column_check)
am_column,pm_column,midday_colum,evening_column

# for COTA ONLY
# pre_early_am_column=[0]  #0 is for Pre-Early AM header
# early_am_column=[1]  #1 is for Early AM header
# # am_column=[2] #2 is for AM header
# am_column=[1] #1 is for AM header
# midday_colum=[2] #2 is for MIDDAY header
# pm_column=[3] #3 is for PM header
# evening_column=[4] #4 is for EVENING header


# Creating new dataframe for specifically AM, PM, MIDDAY, Evenving data and added values from Compeletion Report
new_df=pd.DataFrame()
new_df['ROUTE_SURVEYEDCode']=cr_df['LS_NAME_CODE']
# new_df['CR_Pre_Early_AM']=cr_df[pre_early_am_column[0]]
# new_df['CR_Early_AM']=cr_df[early_am_column[0]]
new_df['CR_AM_Peak']=cr_df[am_column[0]]
new_df['CR_Midday']=cr_df[midday_colum[0]]
new_df['CR_PM_Peak']=cr_df[pm_column[0]]
new_df['CR_Evening']=cr_df[evening_column[0]]
# new_df['Overall Goal']=cr_df[overall_goal_column[0]]
new_df.fillna(0,inplace=True)



# adding values for AM, PM, MIDDAY and Evening from Database file to new Dataframe
for index, row in new_df.iterrows():
    route_code = row['ROUTE_SURVEYEDCode']
    
    # Define a function to get the counts and IDs
    def get_counts_and_ids(time_values):
        subset_df = df[(df['ROUTE_SURVEYEDCode'] == route_code) & (df[time_column[0]].isin(time_values))]
        count = subset_df.shape[0]
        ids = subset_df['id'].values
        return count, ids
    
    # Calculate counts and IDs for each time slot
    am_value, am_value_ids = get_counts_and_ids(am_values)
    midday_value, midday_value_ids = get_counts_and_ids(midday_values)
    pm_value, pm_value_ids = get_counts_and_ids(pm_values)
    evening_value, evening_value_ids = get_counts_and_ids(evening_values)
    
    # Assign values to new_df
    new_df.loc[index, 'CR_Total'] = row['CR_AM_Peak'] + row['CR_Midday'] + row['CR_PM_Peak'] + row['CR_Evening']
    new_df.loc[index, 'DB_AM_Peak'] = am_value
    new_df.loc[index, 'DB_Midday'] = midday_value
    new_df.loc[index, 'DB_PM_Peak'] = pm_value
    new_df.loc[index, 'DB_Evening'] = evening_value
    new_df.loc[index, 'DB_Total'] = evening_value + am_value + midday_value + pm_value
    
    # Join the IDs as a comma-separated string
    new_df.loc[index, 'DB_AM_IDS'] = ', '.join(map(str, am_value_ids))
    new_df.loc[index, 'DB_Midday_IDS'] = ', '.join(map(str, midday_value_ids))
    new_df.loc[index, 'DB_PM_IDS'] = ', '.join(map(str, pm_value_ids))
    new_df.loc[index, 'DB_Evening_IDS'] = ', '.join(map(str, evening_value_ids))

# new_df.to_csv('Time Base Comparison(Over All).csv',index=False)

# Route Level Comparison
new_df['ROUTE_SURVEYEDCode_Splited']=new_df['ROUTE_SURVEYEDCode'].apply(lambda x:('_').join(x.split('_')[:-1]) )

# creating new dataframe for ROUTE_LEVEL_Comparison
route_level_df=pd.DataFrame()

unique_routes=new_df['ROUTE_SURVEYEDCode_Splited'].unique()

route_level_df['ROUTE_SURVEYEDCode']=unique_routes

wkday_route_df.rename(columns={'ROUTE_TOTAL':'CR_Overall_Goal','SURVEY_ROUTE_CODE':'ROUTE_SURVEYEDCode'},inplace=True)
wkday_route_df.dropna(subset=['ROUTE_SURVEYEDCode'],inplace=True)
route_level_df=pd.merge(route_level_df,wkday_route_df[['ROUTE_SURVEYEDCode','CR_Overall_Goal']],on='ROUTE_SURVEYEDCode')

# adding values from database file and compeletion report for Route_Level
for index , row in route_level_df.iterrows():
    subset_df=new_df[new_df['ROUTE_SURVEYEDCode_Splited']==row['ROUTE_SURVEYEDCode']]
    # sum_per_route_cr = subset_df[['CR_AM_Peak', 'CR_Midday', 'CR_PM_Peak', 'CR_Evening','CR_Total','Overall Goal']].sum()
    sum_per_route_cr = subset_df[['CR_AM_Peak', 'CR_Midday', 'CR_PM_Peak', 'CR_Evening','CR_Total']].sum()
    sum_per_route_db = subset_df[['DB_AM_Peak', 'DB_Midday', 'DB_PM_Peak', 'DB_Evening','DB_Total']].sum()
    
    # route_level_df.loc[index,'CR_Pre_Early_AM']=sum_per_route_cr['CR_Pre_Early_AM']
    # route_level_df.loc[index,'CR_Early_AM']=sum_per_route_cr['CR_Early_AM']
    route_level_df.loc[index,'CR_AM_Peak']=sum_per_route_cr['CR_AM_Peak']
    route_level_df.loc[index,'CR_Midday']=sum_per_route_cr['CR_Midday']
    route_level_df.loc[index,'CR_PM_Peak']=sum_per_route_cr['CR_PM_Peak']
    route_level_df.loc[index,'CR_Evening']=sum_per_route_cr['CR_Evening']
    route_level_df.loc[index,'CR_Total']=sum_per_route_cr['CR_Total']
    # route_level_df.loc[index,'CR_Overall_Goal']=sum_per_route_cr['Overall Goal']
    
    route_level_df.loc[index,'DB_AM_Peak']=sum_per_route_db['DB_AM_Peak']
    route_level_df.loc[index,'DB_Midday']=sum_per_route_db['DB_Midday']
    route_level_df.loc[index,'DB_PM_Peak']=sum_per_route_db['DB_PM_Peak']
    route_level_df.loc[index,'DB_Evening']=sum_per_route_db['DB_Evening']
    route_level_df.loc[index,'DB_Total']=sum_per_route_db['DB_Total']   
    route_level_df.loc[index,'DB_AM_IDS']=', '.join(str(value) for value in subset_df['DB_AM_IDS'].values)    
    route_level_df.loc[index,'DB_Midday_IDS']=', '.join(str(value) for value in subset_df['DB_Midday_IDS'].values)    
    route_level_df.loc[index,'DB_PM_IDS']=', '.join(str(value) for value in subset_df['DB_PM_IDS'].values)    
    route_level_df.loc[index,'DB_Evening_IDS']=', '.join(str(value) for value in subset_df['DB_Evening_IDS'].values)

# route_level_df.to_csv('Route Level Comparison.csv',index=False)
    
# calculating the difference between values of database and compeletion report for Route_Level
for index, row in route_level_df.iterrows():
    am_peak_diff=row['CR_AM_Peak']-row['DB_AM_Peak']
    midday_diff=row['CR_Midday']-row['DB_Midday']    
    pm_peak_diff=row['CR_PM_Peak']-row['DB_PM_Peak']
    evening_diff=row['CR_Evening']-row['DB_Evening']
    total_diff=row['CR_Total']-row['DB_Total']
    overall_difference=row['CR_Overall_Goal']-row['DB_Total']
    route_level_df.loc[index, 'AM_DIFFERENCE'] = math.ceil(max(0, am_peak_diff))
    route_level_df.loc[index, 'Midday_DIFFERENCE'] = math.ceil(max(0, midday_diff))
    route_level_df.loc[index, 'PM_DIFFERENCE'] = math.ceil(max(0, pm_peak_diff))
    route_level_df.loc[index, 'Evening_DIFFERENCE'] = math.ceil(max(0, evening_diff))
    # route_level_df.loc[index, 'Total_DIFFERENCE'] = math.ceil(max(0, total_diff))
    route_level_df.loc[index, 'Total_DIFFERENCE'] =math.ceil(max(0, am_peak_diff))+math.ceil(max(0, midday_diff))+math.ceil(max(0, pm_peak_diff))+math.ceil(max(0, evening_diff))
    route_level_df.loc[index, 'Overall_Goal_DIFFERENCE'] = math.ceil(max(0,overall_difference))

# generated two deep copies of route_level_df for furthur processing  
comparison_df=copy.deepcopy(route_level_df)
new_route_level_df=copy.deepcopy(route_level_df)

for index , row in comparison_df.iterrows():
    comparison_df.loc[index,'Total_DIFFERENCE']=math.ceil(max(0,(row['CR_Total']-row['DB_Total'])))


route_level_df.to_csv('COTA Route Level Comparison(Total Difference).csv',index=False)

# Reverse Type Logic
    
# getting the required columns from database file
trip_oppo_dir_column_check=['tripinoppodir']
trip_oppo_dir_column=check_all_characters_present(df,trip_oppo_dir_column_check)

route_survey_name_column_check=['routesurveyed']
route_survey_name_column=check_all_characters_present(df,route_survey_name_column_check)

oppo_dir_time_column_check=['oppodirtriptimecode']
oppo_dir_time_column=check_all_characters_present(df,oppo_dir_time_column_check)

trip_code_column_check=['prevtransferscode','nexttransferscode']
trip_code_column=check_all_characters_present(df,trip_code_column_check)
trip_code_column.sort()

prev_trip_route_code_column_check=['tripfirstroutecode','tripsecondroutecode','tripthirdroutecode','tripfourthroutecode']
next_trip_route_code_column_check=['tripnextroutecode','tripafterroutecode','trip3rdroutecode','triplast4thrtecode']
prev_trip_route_code_column=check_all_characters_present(df,prev_trip_route_code_column_check)
next_trip_route_code_column=check_all_characters_present(df,next_trip_route_code_column_check)

values_to_replace = ['-oth-']
df[[*prev_trip_route_code_column, *next_trip_route_code_column]] = df[
    [*prev_trip_route_code_column, *next_trip_route_code_column]
].replace(values_to_replace, np.nan)

# reverse_df=df[df[trip_oppo_dir_column[0]].str.lower()=='yes'][['id',*route_survey_column,*route_survey_name_column]]
reverse_df=df[df[trip_oppo_dir_column[0]].str.lower()=='yes'][['id',*route_survey_column,*route_survey_name_column,*trip_code_column,*prev_trip_route_code_column,*next_trip_route_code_column]]

reverse_df[route_survey_column[0]]=reverse_df[route_survey_column[0]].apply(lambda x: '_'.join(x.split("_")[:-1]))

reverse_df.reset_index(inplace=True,drop=True)

reverse_df[[*prev_trip_route_code_column,*next_trip_route_code_column]].fillna('',inplace=True)


def get_valid_routes(row, route_code_column):
    result_array = reverse_df[reverse_df['id'] == row['id']][route_code_column].values
    values_in_list = result_array[0, :]
    return [value for value in values_in_list if not (pd.isna(value) or value == '')]

def process_route(route, counter_list, counter_prefix):
    counter_list[0] += 1
    rev_prefix=f'Rev-{counter_prefix}'
    random_choice = random.choice([counter_prefix,rev_prefix ])
    values = route_level_df[route_level_df[route_survey_column[0]] == route]['Total_DIFFERENCE'].values  
    # value = int(route_level_df[route_level_df[route_survey_column[0]] == route]['Total_DIFFERENCE'].values)  
    # if value > 0:
    if len(values) > 0:
        value=int(values)
        reverse_df.loc[index, 'Type'] = f'{random_choice}{counter_list[0]}'
        route_level_df.loc[route_level_df[route_survey_column[0]] == route, 'Total_DIFFERENCE'] = value - 1
        return True
    return False

# implemented the logic for handling Type values for all the data where  opossite direction is True
for index, row in reverse_df.iterrows():
    random_value = random.choice([0, 1])
    value = int(route_level_df[route_level_df[route_survey_column[0]] == row[route_survey_column[0]]]['Total_DIFFERENCE'].values)
    prev_trans_value = int(df[df['id'] == row['id']][trip_code_column[1]].values)
    next_trans_value = int(df[df['id'] == row['id']][trip_code_column[0]].values)
    counter = [0]  # Use a list to store the counter value

    if random_value:
        if value > 0:
            reverse_df.loc[index, 'Type'] = 'Reverse'
            route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Total_DIFFERENCE'] = value - 1
        elif prev_trans_value:
            for route in get_valid_routes(row, prev_trip_route_code_column):
                result_value=process_route(route, counter, 'p')
                if result_value:
                    break
                else:
                    reverse_df.loc[index, 'Type'] = f'{random.choice(["p1","Rev-p1"])}'
                    route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Total_DIFFERENCE'] = value - 1
                    break
        elif next_trans_value:
            for route in get_valid_routes(row, next_trip_route_code_column):
                result_value=process_route(route, counter, 'n')
                if result_value:
                    break
                else:
                    reverse_df.loc[index, 'Type'] = f'{random.choice(["n1","Rev-n1"])}'
                    route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Total_DIFFERENCE'] = value - 1
                    break
        else:
            reverse_df.loc[index, 'Type'] = 'Reverse'
    else:
        if prev_trans_value:
            for route in get_valid_routes(row, prev_trip_route_code_column):
                result_value=process_route(route, counter, 'p')
                if result_value:
                    break
                else:
                    reverse_df.loc[index, 'Type'] = f'{random.choice(["p1","Rev-p1"])}'
                    route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Total_DIFFERENCE'] = value - 1
                    break
        elif next_trans_value:
            for route in get_valid_routes(row, next_trip_route_code_column):
                result_value=process_route(route, counter, 'n')
                if result_value:
                    break
                else:
                    reverse_df.loc[index, 'Type'] = f'{random.choice(["n1","Rev-n1"])}'
                    route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Total_DIFFERENCE'] = value - 1
                    break
        else:
            reverse_df.loc[index, 'Type'] = 'Reverse'

all_type_df=copy.deepcopy(reverse_df)

route_level_df=copy.deepcopy(new_route_level_df)

# implemented the logic for handling Type values for all the data where opossite direction is True and difference between database and compeletion report is greater than 0
for index, row in reverse_df.iterrows():
    value=int(route_level_df[route_level_df[route_survey_column[0]] == row[route_survey_column[0]]]['Total_DIFFERENCE'].values)
    overall_value=int(route_level_df[route_level_df[route_survey_column[0]] == row[route_survey_column[0]]]['Overall_Goal_DIFFERENCE'].values)
    prev_trans_value = int(reverse_df[reverse_df['id'] == row['id']][trip_code_column[1]].values)
    next_trans_value = int(reverse_df[reverse_df['id'] == row['id']][trip_code_column[0]].values)
    if value>0: 
        if random.choice([0,1]):
            reverse_df.loc[index,'Type']='Reverse'
            route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Total_DIFFERENCE'] = value - 1
            route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Overall_Goal_DIFFERENCE'] = overall_value - 1
        else:
            if prev_trans_value:
                result_array = reverse_df[reverse_df['id'] == row['id']][prev_trip_route_code_column].values
                values_in_list = result_array[0, :]
                valid_values = [value for value in values_in_list if not (pd.isna(value) or value == '')]
                prev_counter=0
                for route in valid_values:
                    prev_counter+=1
                    value=int(route_level_df[(route_level_df[route_survey_column[0]]==row[route_survey_column[0]])]['Total_DIFFERENCE'].values)
                    if value >0:
                        
                        reverse_df.loc[index,'Type']=f'{random.choice([f"p{prev_counter}",f"Rev-p{prev_counter}"])}'
                        route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]],'Total_DIFFERENCE'] = value - 1
                        route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Overall_Goal_DIFFERENCE'] = overall_value - 1
                        
                        break
            elif next_trans_value:
                result_array = reverse_df[reverse_df['id'] == row['id']][next_trip_route_code_column].values
                values_in_list = result_array[0, :]
                valid_values = [value for value in values_in_list if not (pd.isna(value) or value == '')]
                next_counter=0
                for route in valid_values:
                    next_counter+=1
                    value=int(route_level_df[(route_level_df[route_survey_column[0]]==row[route_survey_column[0]])]['Total_DIFFERENCE'].values)
                    if value >0:
                        reverse_df.loc[index,'Type']=f'{random.choice([f"n{next_counter}",f"Rev-n{next_counter}"])}'
                        route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]],'Total_DIFFERENCE'] = value - 1
                        route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Overall_Goal_DIFFERENCE'] = overall_value - 1
                        break
            else:
                reverse_df.loc[index,'Type']='Reverse'
                route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]],'Total_DIFFERENCE'] = value - 1
                route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Overall_Goal_DIFFERENCE'] = overall_value - 1              
    elif overall_value>0:
        print("Entering in Overall Value")
        print(row['id'])
        reverse_df.loc[index,'Type']='Reverse'
        route_level_df.loc[route_level_df[route_survey_column[0]] == row[route_survey_column[0]], 'Overall_Goal_DIFFERENCE'] = overall_value - 1
    else:
        reverse_df.loc[index,'Type']=''



reverse_df['Type'].fillna('',inplace=True)

reverse_df['COMPLETED By']=''
all_type_df['COMPLETED By']=''

all_type_df['Type'].fillna('Reverse',inplace=True)

# reverse_df['Random']= np.random.randint(1000, 1000000, size=len(reverse_df))

# reverse_df[['id',route_survey_column[0],route_survey_name_column[0],'Type','COMPLETED By']].to_csv('Reverse Routes.csv',index=False)

# route_level_df.to_csv('COTA Route Level Comparison Updated01.csv',index=False)

# creating file with 3 required tabs 
with pd.ExcelWriter('SantaClarita Route Level Comparison(refactor).xlsx') as writer:
    # comparison_df.loc[:, ~comparison_df.columns.isin(['Total_DIFFERENCE'])].to_excel(writer,sheet_name='Route Comparison',index=False)
    comparison_df.drop(columns=['Total_DIFFERENCE']).to_excel(writer,sheet_name='Route Comparison',index=False)
    all_type_df[['id',route_survey_column[0],route_survey_name_column[0],'Type','COMPLETED By']].to_excel(writer,sheet_name='Reverse Routes',index=False)
    reverse_df[reverse_df['Type']!=''][['id',route_survey_column[0],route_survey_name_column[0],'Type','COMPLETED By']].to_excel(writer,sheet_name='Reverse Routes Difference',index=False)

print("Files Generated SuccessFully")