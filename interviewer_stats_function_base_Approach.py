import pandas as pd
import numpy as np
from geopy.distance import geodesic
import math
from datetime import date

import warnings

warnings.filterwarnings('ignore')

today_date = date.today()
today_date=''.join(str(today_date).split('-'))
project_name='BART'

excel_file = 'BART_CA_KINGElvis (3).xlsx'

df=pd.read_csv('elvisbartca2024interceptNEW_main_export_odbc(001).csv')
elvis_df= pd.read_excel(excel_file, sheet_name='Elvis_Review')

df=df[(df['INTERV_INIT']!='999')]
df = df[(df['HAVE_5_MIN_FOR_SURVECode'] == 1)]

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


# Interviewer Location Code Starts here

for _,row in df.iterrows():
    for i in range(1,7):
        
        if not pd.isna(row[f'ELVIS_USER_LOC{i}_LAT']) and not pd.isna(row[f'ELVIS_USER_LOC{i}_LONG']):
            df.loc[row.name,'ELVIS_USER_LOC_LAT']=row[f'ELVIS_USER_LOC{i}_LAT']
            df.loc[row.name,'ELVIS_USER_LOC_LONG']=row[f'ELVIS_USER_LOC{i}_LONG']
            break
        else:
            df.loc[row.name,'ELVIS_USER_LOC_LAT']=np.nan
            df.loc[row.name,'ELVIS_USER_LOC_LONG']=np.nan

df['Distances'] = 0
# df['Distances'] = -1

# Get unique INTERV_INIT values
unique_interv_init = df['INTERV_INIT'].unique()
unique_interv_init

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
        return -1
    


# Loop through each unique INTERV_INIT value
for interv in unique_interv_init:
    # Filter rows where INTERV_INIT matches the current unique value
    df_filtered = df[df['INTERV_INIT'] == interv]
    df_filtered.sort_values(by='id',ascending=True,inplace=True)
    
    # If only one row is present, keep the distance as -1
    if len(df_filtered) == 1:
        continue
    
    # Calculate the geodesic distance between consecutive rows
    distances = [0]  # Start with 0 for the first row

    for i in range(1, len(df_filtered)):
        # Get the coordinates for the current and previous row
        coords_1 = (df_filtered.iloc[i - 1]['ELVIS_USER_LOC_LAT'], df_filtered.iloc[i - 1]['ELVIS_USER_LOC_LONG'])
        coords_2 = (df_filtered.iloc[i]['ELVIS_USER_LOC_LAT'], df_filtered.iloc[i]['ELVIS_USER_LOC_LONG'])
        # Calculate distance using geopy
        distance = get_distance_between_coordinates(df_filtered.iloc[i - 1]['ELVIS_USER_LOC_LAT'], df_filtered.iloc[i - 1]['ELVIS_USER_LOC_LONG'],df_filtered.iloc[i]['ELVIS_USER_LOC_LAT'],df_filtered.iloc[i]['ELVIS_USER_LOC_LONG'])
        distances.append(round(distance,4))
    
    # Update the distances in the original DataFrame
    df.loc[df['INTERV_INIT'] == interv, 'Distances'] = distances


for interv in unique_interv_init:
    df_filtered = df[df['INTERV_INIT'] == interv]
    df_filtered.sort_values(by='id', ascending=True, inplace=True)

    distances = df_filtered['Distances'].values
    flags = [0] * len(distances)  # Initialize all flags to 0

    # Loop through the Distances column and check differences
    for i in range(len(distances) - 3):  # Ensure we have at least 4 points
        # Calculate differences between consecutive distances
        diff_1 = abs(distances[i+1] - distances[i])
        diff_2 = abs(distances[i+2] - distances[i+1])
        diff_3 = abs(distances[i+3] - distances[i+2])

        # If all three consecutive differences are less than 0.25, flag all 4 surveys
        if diff_1 < 0.25 and diff_2 < 0.25 and diff_3 < 0.25:
            flags[i] = 1
            flags[i+1] = 1
            flags[i+2] = 1
            flags[i+3] = 1

    # Assign the flags to a new column in the original DataFrame
    df.loc[df['INTERV_INIT'] == interv, 'Consecutive_Flag'] = flags



# df[['id','INTERV_INIT','ELVIS_USER_LOC_LAT', 'ELVIS_USER_LOC_LONG','Distances','Consecutive_Flag']].to_csv('Interviewer_Survey_Distances.csv',index=False)


# distance_df=df[['id', 'INTERV_INIT', 'Survey Date', 'ELVIS_USER_LOC_LAT',
#        'ELVIS_USER_LOC_LONG', 'Distances', 'Consecutive_Flag']]

# Interviewer TimeStamp Code Starts Here

timestamp_columns_check=['completed','reviewscrtime','homeaddtime']
timestamp_columns=check_all_characters_present(df,timestamp_columns_check)
timestamp_columns.sort()

df[timestamp_columns[0]]=pd.to_datetime(df[timestamp_columns[0]], errors='coerce')
df[timestamp_columns[1]]=pd.to_datetime(df[timestamp_columns[1]], errors='coerce')
df[timestamp_columns[2]]=pd.to_datetime(df[timestamp_columns[2]], errors='coerce')

df['Full Survey Time'] = ''
df['Field Reviewed'] = ''
# Calculate minutes for Logistics Time
df['Logistics Time'] = (df[timestamp_columns[0]]- df[timestamp_columns[1]]).dt.total_seconds() / 60
# Calculate minutes for Demographic Time
df['Demographic Time'] = ( df[timestamp_columns[2]] - df[timestamp_columns[1]]).dt.total_seconds() / 60
df['Survey Date'] = df['Completed'].dt.date

# Adding Consecutive_Flag So that I Can Calculate the Location Distance Percentage
timestamp_df=df[['id','INTERV_INIT','Survey Date','Full Survey Time','Logistics Time','Demographic Time','Field Reviewed','Consecutive_Flag']]
timestamp_df['Full Survey Time']=timestamp_df['Logistics Time']+timestamp_df['Demographic Time']

timestamp_df['Full Survey Time Flag'] = (timestamp_df['Full Survey Time'] < 4).astype(int)
timestamp_df['Logistics Time Flag'] = (timestamp_df['Logistics Time'] < 2).astype(int)
timestamp_df['Demographic Time Flag'] = (timestamp_df['Demographic Time'] < 2).astype(int)
# INTERVIEWER TimeStampData: Full Survey Time, Logistics Time, Demographic Time
# timestamp_df.to_csv("INTERVIEWER_TIMESTAMP.csv",index=False)


# INTERVIEWER TimeStamp Summary code starts Here

# Overall Interviewer TimeStamp Summary code starts Here
unique_interv=df['INTERV_INIT'].unique()

def over_all_data_df_creation(unique_interv,timestamp_df):

    over_all_data=[]
    for user in unique_interv:
        total_records=timestamp_df[timestamp_df['INTERV_INIT']==user].shape[0]    
        full_time_survey=timestamp_df[(timestamp_df['INTERV_INIT']==user)&(timestamp_df['Full Survey Time Flag']==1)].shape[0]    
        logistic_time_survey=timestamp_df[(timestamp_df['INTERV_INIT']==user)&(timestamp_df['Logistics Time Flag']==1)].shape[0]    
        demographic_time_survey=timestamp_df[(timestamp_df['INTERV_INIT']==user)&(timestamp_df['Demographic Time Flag']==1)].shape[0]\
        # Calculating distance Flag so have to drop this colum while saving it to file
        location_distance_survey=timestamp_df[(timestamp_df['INTERV_INIT']==user)&(timestamp_df['Consecutive_Flag']==1)].shape[0]

        full_time_survey_percentage = round((full_time_survey / total_records) * 100,2) if total_records != 0 else 0
        logistic_time_survey_percentage = round((logistic_time_survey / total_records) * 100,2) if total_records != 0 else 0
        demographic_time_survey_percentage = round((demographic_time_survey / total_records) * 100,2) if total_records != 0 else 0
        location_distance_survey_percentage = round((location_distance_survey / total_records) * 100,2) if total_records != 0 else 0
        
        # Append results to the list
        over_all_data.append({
            'INTERV_INIT': user,
            'Total Records': total_records,
            'Full Time Survey Records': full_time_survey,
            'Logistic Time Survey Records': logistic_time_survey,
            'Demographic Time Survey Records': demographic_time_survey,
            'Full Time Survey Percentage': full_time_survey_percentage,
            'Logistic Time Survey Percentage': logistic_time_survey_percentage,
            'Demographic Time Survey Percentage': demographic_time_survey_percentage,
            'Location Distance Percentage': location_distance_survey_percentage,
        })
    return over_all_data

over_all_data=over_all_data_df_creation(unique_interv,timestamp_df)

over_all_data_df=pd.DataFrame(over_all_data)
# Overall Interviewer TimeStamp Summary code ENDS Here

# Date/Daily Interviewer TimeStamp Summary


def daily_timestamp_data_df_creation(unique_interv,timestamp_df):
    daily_timestamp_data = []
    for user in unique_interv:

        user_data = timestamp_df[timestamp_df['INTERV_INIT'] == user]
        

        unique_dates = user_data['Survey Date'].unique()
        

        for date in unique_dates:
            date_data = user_data[user_data['Survey Date'] == date]
            total_records = date_data.shape[0]

            full_time_survey = date_data[date_data['Full Survey Time Flag'] == 1].shape[0]
            logistic_time_survey = date_data[date_data['Logistics Time Flag'] == 1].shape[0]
            demographic_time_survey = date_data[date_data['Demographic Time Flag'] == 1].shape[0]
            
            # Calculate percentages
            full_time_survey_percentage =  round((full_time_survey / total_records) * 100,2) if total_records != 0 else 0
            logistic_time_survey_percentage = round((logistic_time_survey / total_records) * 100,2) if total_records != 0 else 0
            demographic_time_survey_percentage =  round((demographic_time_survey / total_records) * 100,2) if total_records != 0 else 0
            
            # Append results to the list
            daily_timestamp_data.append({
                'INTERV_INIT': user,
                'Survey Date': date,
                'Total Records': total_records,
                'Full Time Survey Records': full_time_survey,
                'Logistic Time Survey Records': logistic_time_survey,
                'Demographic Time Survey Records': demographic_time_survey,
                'Full Time Survey Percentage': full_time_survey_percentage,
                'Logistic Time Survey Percentage': logistic_time_survey_percentage,
                'Demographic Time Survey Percentage': demographic_time_survey_percentage
            })
    return daily_timestamp_data

daily_timestamp_data=daily_timestamp_data_df_creation(unique_interv,timestamp_df)
daily_timestamp_data_df=pd.DataFrame(daily_timestamp_data)
# Date/Daily Interviewer TimeStamp Summary code ENDS Here

# Interviewer Daily Percentage Code Starts Here

def daily_user_location_data_df_creation(df):
    daily_user_location_data = []
    unique_interv = df['INTERV_INIT'].unique()

    for user in unique_interv:
        all_records=0
        flag_records=0
        user_data = df[df['INTERV_INIT'] == user]
        

        unique_dates = user_data['Survey Date'].unique()
        

        for date in unique_dates:
            
            date_data = user_data[user_data['Survey Date'] == date]
            total_records = date_data.shape[0]
            
            consecutive_flag = date_data[date_data['Consecutive_Flag'] == 1].shape[0]
            
            all_records+=total_records
            flag_records+=consecutive_flag
            # Calculate percentages
            consecutive_flag_percentage =  round((consecutive_flag / total_records) * 100,2) if total_records != 0 else 0
            
            # Append results to the list
            daily_user_location_data.append({
                'INTERV_INIT': user,
                'Survey Date': date,
                '# of Surveys': total_records,
                '# of Consecutive_Flag': consecutive_flag,
                'Consective Flags Percentage': consecutive_flag_percentage,

            })
        if all_records and flag_records:
            daily_user_location_data.append({
                'INTERV_INIT': user+' Total',
                'Survey Date': pd.NaT,
                '# of Surveys': all_records,
                '# of Consecutive_Flag': flag_records,
                'Consective Flags Percentage': round((flag_records/all_records)*100,2),

            })
    return daily_user_location_data

daily_user_location_data=daily_user_location_data_df_creation(df)
daily_user_location_data_df=pd.DataFrame(daily_user_location_data)

# Interviewer Daily Percentage Code ENDS Here

# Interviewer Information Code Starts Here

# Group by 'INTERV_INIT' and count unique 'id' values for each group
id_count_per_interv_init = df.groupby('INTERV_INIT')['id'].nunique().reset_index(name='id_count')

# Prepare to store results for each 'INTERV_INIT'
results = []

# Loop through each 'INTERV_INIT' group and count 'Final_Usage' as 'Remove'
for index, row in id_count_per_interv_init.iterrows():
    interv_init_value = row['INTERV_INIT']
    valid_ids = df[df['INTERV_INIT'] == interv_init_value]['id'].unique()

    # Filter Excel file for those valid ids and 'Final_Usage' as 'Remove'
    remove_count = elvis_df[(elvis_df['id'].isin(valid_ids)) & (elvis_df['Final_Usage']  == 'Remove')]['id'].nunique()

    # Calculate percentage of ids with 'Final_Usage' as 'Remove'
    if row['id_count'] > 0:
        remove_percentage = (remove_count / row['id_count']) * 100
    else:
        remove_percentage = 0

    # Append result for this 'INTERV_INIT' group
    results.append({
        'INTERV_INIT': interv_init_value,
        'Valid_IDs_Count': row['id_count'],
        'Remove_IDs_Count': remove_count,
        'Remove_Percentage': remove_percentage
    })

interviewer_info_df = pd.DataFrame(results)
# Interviewer Information Code ENDS Here


# Combine TimeStamp and Location Distance Data Code Starts here
time_stamp_data = []

# Loop through each unique user
for user in unique_interv:
    # Filter records for the current user
    user_data = timestamp_df[timestamp_df['INTERV_INIT'] == user]
    
    # Get unique survey dates for this user
    unique_dates = user_data['Survey Date'].unique()
    
    # Loop through each unique date
    for date in unique_dates:
        # Filter records for the specific date
        date_data = user_data[user_data['Survey Date'] == date]
        
        # Dictionary to store flagged records for each type
        flag_ids = {
            'Full Survey Time': date_data[date_data['Full Survey Time Flag'] == 1]['id'].values,
            'Logistic Time': date_data[date_data['Logistics Time Flag'] == 1]['id'].values,
            'Demographic Time': date_data[date_data['Demographic Time Flag'] == 1]['id'].values
        }

        # Append data to new_data list for each flag type
        for flag_type, ids in flag_ids.items():
            time_stamp_data.append({
                'INTERV_INIT': user,
                'Survey Date': date,
                'Full Survey Time': len(ids) if flag_type == 'Full Survey Time' else np.nan,
                'Logistic Time': len(ids) if flag_type == 'Logistic Time' else np.nan,
                'Demographic Time': len(ids) if flag_type == 'Demographic Time' else np.nan,
                'IDS': ids
            })
time_stamp_new_df = pd.DataFrame(time_stamp_data)

distance_df=df[['id', 'INTERV_INIT', 'Survey Date', 'ELVIS_USER_LOC_LAT',
       'ELVIS_USER_LOC_LONG', 'Distances', 'Consecutive_Flag']]

location_distance_data=[]
for user in unique_interv:
    # Get all records for the user
    user_data = distance_df[distance_df['INTERV_INIT'] == user]
    
    # Get unique dates for this user
    unique_dates = user_data['Survey Date'].unique()
    
    # Iterate through each unique date
    for date in unique_dates:
        # Get all records for the user on that specific date
        date_data = user_data[user_data['Survey Date'] == date]
        
        # Get total records for the user on that specific date
        total_records = date_data.shape[0]
        
        # Get flagged records for each type on that specific date
        distance_flags_survey_ids = date_data[date_data['Consecutive_Flag'] == 1]['id'].values
        
        location_distance_data.append({
                'INTERV_INIT': user,
                'Survey Date': date,
                'Distance Between Survey Locations': len(distance_flags_survey_ids),
                'IDS': distance_flags_survey_ids
            })

location_distance_df=pd.DataFrame(location_distance_data)
empty_columns = pd.DataFrame(np.nan, index=time_stamp_new_df.index, columns=[None] * 3) 
combine_time_distance_summary=pd.concat([time_stamp_new_df,empty_columns,location_distance_df],axis=1)
# Combine TimeStamp and Location Distance Data Code ENDS here

# Overall df Summary Code starts here
filtered_user_location_data_df = daily_user_location_data_df[~daily_user_location_data_df['INTERV_INIT'].str.contains('Total', case=False, na=False)]

daily_timedistance_df=pd.merge(filtered_user_location_data_df, daily_timestamp_data_df, on=['INTERV_INIT', 'Survey Date'])


# Code for One Line Summary Where Overall percentage is greater than 25
def daily_percentage_oneline_summary(daily_timedistance_df):
    unique_interv = daily_timedistance_df['INTERV_INIT'].unique()
    summary_data = []

    for user in unique_interv:
        user_data = daily_timedistance_df[daily_timedistance_df['INTERV_INIT'] == user]
        total_records = 0
        full_time_flag_records = 0
        logistic_time_flag_records = 0
        demographic_time_flag_records = 0
        consecutive_flag_records = 0
        full_time_counter = 0
        logistic_time_counter = 0
        demographic_time_counter = 0
        consecutive_counter = 0
        full_time_total_percentage=0
        logistic_time_total_percentage=0
        demographic_time_total_percentage=0
        consecutive_flag_total_percentage=0
        
        unique_dates = user_data['Survey Date'].unique()
        total_days = len(unique_dates)
        
        for date in unique_dates:
            daily_data = user_data[user_data['Survey Date'] == date]
            total_records += daily_data['# of Surveys'].sum()
            
            # Check for full time flag records
            full_time_records = daily_data['Full Time Survey Records'].sum()
            full_time_percentage=daily_data['Full Time Survey Percentage'].sum()
            if full_time_records > 0 and full_time_percentage>25:
                full_time_counter += 1
                full_time_total_percentage+=full_time_percentage
                full_time_flag_records += full_time_records
            
            # Check for logistic time flag records
            logistic_time_records = daily_data['Logistic Time Survey Records'].sum()
            logistic_time_percentage=daily_data['Logistic Time Survey Percentage'].sum()
            if logistic_time_records > 0 and logistic_time_percentage>25:
                logistic_time_total_percentage+=logistic_time_percentage
                logistic_time_counter += 1
                logistic_time_flag_records += logistic_time_records
            
            # Check for demographic time flag records
            demographic_time_records = daily_data['Demographic Time Survey Records'].sum()
            demographic_time_percentage=daily_data['Demographic Time Survey Percentage'].sum()
            if demographic_time_records > 0 and demographic_time_percentage>25:
                demographic_time_total_percentage+=demographic_time_percentage
                demographic_time_flag_records += demographic_time_records
                demographic_time_counter += 1
            
            # Check for consecutive flag records
            consecutive_flags = daily_data['# of Consecutive_Flag'].sum()
            consecutive_percentage=daily_data['Consective Flags Percentage'].sum()
            if consecutive_flags > 0 and consecutive_percentage>25:
                consecutive_flag_total_percentage+=consecutive_percentage
                consecutive_flag_records += consecutive_flags
                consecutive_counter += 1
        
        if total_records > 0:
    #         full_time_flag_per=round((full_time_flag_records / total_records) * 100, 2)
    #         logistic_time_flag_per=round((logistic_time_flag_records / total_records) * 100, 2)
    #         demographic_time_flag_per=round((demographic_time_flag_records / total_records) * 100, 2)
    #         consecutive_flag_per=round((consecutive_flag_records / total_records) * 100, 2)
            description = (
                f"Summary for Interviewer {user}:\n"
                f"- Total Records: {total_records}\n"
                f"- {full_time_counter} out of {total_days} days had flags > 25% affecting {round(full_time_total_percentage/full_time_counter,2) if full_time_counter > 0 else 0}% of full survey records completed in under 4 minutes.\n"
                f"- {logistic_time_counter} out of {total_days} days had flags > 25% affecting {round(logistic_time_total_percentage/logistic_time_counter,2) if logistic_time_counter > 0 else 0}% of logistic part records completed in under 2 minutes.\n"
                f"- {demographic_time_counter} out of {total_days} days had flags > 25% affecting {round(demographic_time_total_percentage/demographic_time_counter,2) if demographic_time_counter > 0 else 0}% of demographic part records completed in under 2 minutes.\n"
                f"- {consecutive_counter} out of {total_days} days had flags > 25% affecting {round(consecutive_flag_total_percentage/consecutive_counter,2) if consecutive_counter > 0 else 0}% consecutive flags."
            )
        else:
            description = f"Summary for Interviewer {user}:\n- No records found."
        
        counters = [full_time_counter, logistic_time_counter, demographic_time_counter, consecutive_counter]

        # Count the number of non-zero values
        non_zero_count = sum(1 for count in counters if count > 0)
        
        summary_data.append({
            'INTERV_INIT': user,
            'Total_Flags':non_zero_count,
            'Description': description
        })

    summary_data_df = pd.DataFrame(summary_data)
    return summary_data_df



def overall_percentage_oneline_summary(daily_timedistance_df):
    unique_interv = daily_timedistance_df['INTERV_INIT'].unique()
    summary_data = []
    for user in unique_interv:
        user_data = daily_timedistance_df[daily_timedistance_df['INTERV_INIT'] == user]
        total_records = 0
        full_time_flag_records = 0
        logistic_time_flag_records = 0
        demographic_time_flag_records = 0
        consecutive_flag_records = 0
        full_time_counter = 0
        logistic_time_counter = 0
        demographic_time_counter = 0
        consecutive_counter = 0
        
        unique_dates = user_data['Survey Date'].unique()
        total_days = len(unique_dates)
        
        for date in unique_dates:
            daily_data = user_data[user_data['Survey Date'] == date]
            total_records += daily_data['# of Surveys'].sum()
            
            # Check for full time flag records
            full_time_records = daily_data['Full Time Survey Records'].sum()
            if full_time_records > 0:
                full_time_counter += 1
                full_time_flag_records += full_time_records
            
            # Check for logistic time flag records
            logistic_time_records = daily_data['Logistic Time Survey Records'].sum()
            if logistic_time_records > 0:
                logistic_time_counter += 1
                logistic_time_flag_records += logistic_time_records
            
            # Check for demographic time flag records
            demographic_time_records = daily_data['Demographic Time Survey Records'].sum()
            if demographic_time_records > 0:
                demographic_time_flag_records += demographic_time_records
                demographic_time_counter += 1
            
            # Check for consecutive flag records
            consecutive_flags = daily_data['# of Consecutive_Flag'].sum()
            if consecutive_flags > 0:
                consecutive_flag_records += consecutive_flags
                consecutive_counter += 1
        
        if total_records > 0:
            full_time_flag_per=round((full_time_flag_records / total_records) * 100, 2)
            logistic_time_flag_per=round((logistic_time_flag_records / total_records) * 100, 2)
            demographic_time_flag_per=round((demographic_time_flag_records / total_records) * 100, 2)
            consecutive_flag_per=round((consecutive_flag_records / total_records) * 100, 2)
            # Initialize the description with a summary line
            description = f"Summary for Interviewer {user}:\n- Total Records: {total_records}\n"

            # Add full-time flag details
            if full_time_flag_per > 25:
                description += f"- {full_time_counter} out of {total_days} days had {full_time_flag_per}% of full survey records completed in under 4 minutes.\n"
            else:
                full_time_counter = 0
                full_time_flag_per = 0
                description += f"- {full_time_counter} out of {total_days} days had {full_time_flag_per}% of full survey records completed in under 4 minutes.\n"

            # Add logistic-time flag details
            if logistic_time_flag_per > 25:
                description += f"- {logistic_time_counter} out of {total_days} days had {logistic_time_flag_per}% of logistic part records completed in under 2 minutes.\n"
            else:
                logistic_time_counter = 0
                logistic_time_flag_per = 0
                description += f"- {logistic_time_counter} out of {total_days} days had {logistic_time_flag_per}% of logistic part records completed in under 2 minutes.\n"

            # Add demographic-time flag details
            if demographic_time_flag_per > 25:
                description += f"- {demographic_time_counter} out of {total_days} days had {demographic_time_flag_per}% of demographic part records completed in under 2 minutes.\n"
            else:
                demographic_time_counter = 0
                demographic_time_flag_per = 0
                description += f"- {demographic_time_counter} out of {total_days} days had {demographic_time_flag_per}% of demographic part records completed in under 2 minutes.\n"

            # Add consecutive flag details
            if consecutive_flag_per > 25:
                description += f"- {consecutive_counter} days had {consecutive_flag_per}% consecutive flags."
            else:
                consecutive_counter = 0
                consecutive_flag_per = 0
                description += f"- {consecutive_counter} days had {consecutive_flag_per}% consecutive flags."
        else:
            description = f"Summary for Interviewer {user}:\n- No records found."
        
        counters = [full_time_counter, logistic_time_counter, demographic_time_counter, consecutive_counter]

        # Count the number of non-zero values
        non_zero_count = sum(1 for count in counters if count > 0)
        
        summary_data.append({
            'INTERV_INIT': user,
            'Total_Flags':non_zero_count,
            'Description': description
        })

    summary_data_df = pd.DataFrame(summary_data)
    return summary_data_df


summary_data_df=overall_percentage_oneline_summary(daily_timedistance_df)
# grouped = over_all_data_df.groupby('INTERV_INIT').agg(
#     Total_Records=('Total Records', 'sum'),
#     Full_Time_Records_Percent=('Full Time Survey Percentage', 'mean'),
#     Logistic_Time_Records_Percent=('Logistic Time Survey Percentage', 'mean'),
#     Demographic_Time_Records_Percent=('Demographic Time Survey Percentage', 'mean'),
#     Location_Distance_Time_Records_Percent=('Location Distance Percentage', 'mean'),
#     Full_Time_Days_Over_25_Percent=('Full Time Survey Percentage', lambda x: (x > 25).mean() * 100),
#     Logistic_Time_Days_Over_25_Percent=('Logistic Time Survey Percentage', lambda x: (x > 25).mean() * 100),
#     Demographic_Time_Days_Over_25_Percent=('Demographic Time Survey Percentage', lambda x: (x > 25).mean() * 100),
#     Location_Distance_Time_Days_Over_25_Percent=('Location Distance Percentage', lambda x: (x > 25).mean() * 100)
# ).reset_index()
# def create_summary(row):
#     description = (
#         f"Summary for Interviewer {row['INTERV_INIT']}:\n"
#         f"- Total Records: {row['Total_Records']}\n"
#         f"- {row['Full_Time_Records_Percent']:.1f}% of full survey records were completed in under 4 minutes.\n"
#         f"- {row['Logistic_Time_Records_Percent']:.1f}% of logistic part records were completed in under 2 minutes.\n"
#         f"- {row['Demographic_Time_Records_Percent']:.1f}% of demographic part records were completed in under 2 minutes.\n"
#         f"- {row['Location_Distance_Time_Records_Percent']:.1f}% of records were conducted within 0.25 miles of the previous survey."
#     )
#     return description

# # Apply the summary function to each row
# grouped['Description'] = grouped.apply(create_summary, axis=1)

# Overall df Summary Code ENDS here


with pd.ExcelWriter(f'reviewtool_{today_date}_{project_name}_interviewerstats.xlsx') as writer:
    # grouped[['INTERV_INIT','Description']].to_excel(writer, sheet_name="INTERV One Line Summary", index=False)
    summary_data_df.to_excel(writer, sheet_name="INTERV One Line Summary", index=False)
    combine_time_distance_summary.to_excel(writer, sheet_name="INTERV TimeDistance Summary", index=False)
    #Have to remove Consecutive_Flag because it was Added So that I Can Calculate the Location Distance Percentage
    timestamp_df.drop(columns=['Consecutive_Flag']).to_excel(writer, sheet_name="INTERV TimeStamp Checks", index=False)
    daily_user_location_data_df.to_excel(writer,'INTERV Daily Distance Checks',index=False)
    df[['id','INTERV_INIT','Survey Date','ELVIS_USER_LOC_LAT', 'ELVIS_USER_LOC_LONG','Distances','Consecutive_Flag']].to_excel(writer, sheet_name="INTERV Distance Checks", index=False)
    daily_timestamp_data_df.to_excel(writer, sheet_name="INTERV Daily TimeStamp Summary", index=False)
    over_all_data_df.drop(columns=['Location Distance Percentage']).to_excel(writer, sheet_name="INTERV Overall Time Summary", index=False)
    interviewer_info_df.to_excel(writer, sheet_name="INTERV Information", index=False)



print("File Generated Successfully")