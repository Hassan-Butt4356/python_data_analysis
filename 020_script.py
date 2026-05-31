import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import copy
from pprint import pprint

warnings.filterwarnings('ignore')


def check_all_code_columns(df, columns_to_check):
    # Function to clean a string by removing underscores and square brackets and converting to lowercase
    def clean_string(s):
        return s.replace('_', '').replace('[', '').replace(']', '').replace(' ','').replace('#','').lower()

    # Clean and convert all column names in df to lowercase for case-insensitive comparison
    df_columns_lower = [clean_string(column) for column in df.columns]

    # Clean and convert the columns_to_check list to lowercase for case-insensitive comparison
    columns_to_check_lower = [clean_string(column) for column in columns_to_check]

    # Use a list comprehension to filter columns
    matching_columns = [column for column in df_columns_lower if "code" in column]

    return matching_columns


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

def clean_string(s):
    return s.replace(':', '').replace('-', '').replace('_', '').replace('[', '').replace(']', '').replace(' ','').replace('#','').lower()

project_name='VTA'

df=pd.read_csv('vtaca2024rail_o2o_export_odbc.csv')

# df=df[df['INTERV_INIT']!='999']

detail_df=pd.read_excel('details_vta_CA_od_excel (1).xlsx',sheet_name='STOPS')

code_columns=check_all_code_columns(df,df.columns)

code_columns=check_all_characters_present(df,code_columns)


o2o_df=copy.deepcopy(df)

date_columns_check=['completed']
date_columns=check_all_characters_present(o2o_df,date_columns_check)

def get_day_name(x):
    try:
        date_object = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        date_object = datetime.strptime(x, '%d/%m/%Y %H:%M')
    day_name = date_object.strftime('%A')
    if day_name in ['Saturday', 'Sunday']:
        return 'Weekend'
    return 'Weekday'

# o2o_df[date_columns[0]].fillna(method='ffill',inplace=True)
# o2o_df[date_columns[0]] = o2o_df[date_columns[0]].astype(str)

o2o_df['Day']=o2o_df[date_columns[0]].apply(get_day_name)


owl_values=['100am']
am_values=['600am','700am','800am']
midday_values=['900am','1000','1100am','1200pm','100pm']
pm_values=['200pm','300pm']
pm_peak_values=['400pm','500pm','600pm']
eve_values=['700pm','800pm','900pm']
night_values=['1000pm']

def get_start_time(x):
    return clean_string(x.split('-')[0])

o2o_df['Start_Time']=o2o_df['TIME_BOARDED'].apply(get_start_time)

time_period_mapping = {
    'AM': am_values,
    'MIDDAY': midday_values,
    'PM': pm_values,
    'PM PEAK': pm_peak_values,
    'EVE': eve_values,
    'NIGHT': night_values
}

for index, row in o2o_df.iterrows():
    for period, values in time_period_mapping.items():
        if row['Start_Time'] in values:
            o2o_df.at[index, 'TIME PERIOD'] = period
            o2o_df.at[index, 'TIME PERIOD[CODE]'] = list(time_period_mapping.keys()).index(period)
            break
    else:
        o2o_df.at[index, 'TIME PERIOD'] = 'OWL'
        o2o_df.at[index, 'TIME PERIOD[CODE]'] = len(time_period_mapping)

o2o_df.drop(columns=['Start_Time'],inplace=True)

# above code is working fine

def remove_1st_char(x):
    x=clean_string(str(x))
    if type(x)==str:
        return float(x[-4:])
    return float(str(x)[1:])

def combine_route_and_stop(route_value,stop_value):
    return route_value+'_'+str(int(stop_value))


def remove_code_name(x,df):
    x=clean_string(x)[:-4]
    x=check_all_characters_present(df,[x])
    return x[0]


columns_to_remove=[]
for column in code_columns:
    cleaned_column=clean_string(column)
#     if 'routesurveyed' in cleaned_column or 'language' in cleaned_column:
    if 'time' in cleaned_column or 'language' in cleaned_column:
        columns_to_remove.append(column)




new_df=o2o_df.drop(columns=columns_to_remove)

code_columns_check=check_all_characters_present(new_df,code_columns)

new_code_columns=check_all_characters_present(new_df,code_columns_check)

# print(new_df['TIME PERIOD[CODE]'][0])

# exit()

for _,row in new_df.iterrows():
    counter=0
    for i in range(1,len(new_code_columns)):
        value=row[code_columns[i]]
        if not pd.isnull(value):
            stop_value=remove_1st_char(value)
            route_value=row[code_columns[0]]
            combine_value=combine_route_and_stop(route_value,stop_value)
            matched_value=detail_df[(detail_df['ETC_ROUTE_ID']==route_value)&(detail_df['ETC_STOP_ID']==combine_value)]
            if not matched_value.empty:
                counter+=1
                if counter==1:
                    new_df.loc[row.name, ['ROUTE_DESCRIPTION[CODE]','BOARD_ID', 'BOARD_STOP[CODE]', 'BOARD_STOP_NAME', 'BOARD_LAT', 'BOARD_LONG']] = [
                        matched_value.iloc[0]['ETC_ROUTE_ID'], 
                        matched_value.iloc[0]['stop_id'], 
                        matched_value.iloc[0]['ETC_STOP_ID'], 
                        matched_value.iloc[0]['ETC_STOP_NAME'], 
                        matched_value.iloc[0]['stop_lat6'], 
                        matched_value.iloc[0]['stop_lon6']
                        ]
                if counter>1:
                    new_df.loc[row.name, ['ALIGHT_ID', 'ALIGHT_STOP[CODE]', 'ALIGHT_STOP_NAME', 'ALIGHT_LAT', 'ALIGHT_LONG']] = [matched_value.iloc[0]['stop_id'], 
                        matched_value.iloc[0]['ETC_STOP_ID'], 
                        matched_value.iloc[0]['ETC_STOP_NAME'], 
                        matched_value.iloc[0]['stop_lat6'], 
                        matched_value.iloc[0]['stop_lon6']]



new_df=pd.merge(new_df,o2o_df[['id','TIME_BOARDED_Code_']],on='id',how='left')

# 'routesurveyedcode','routesurveyed',

columns_to_include_check=['id','completed','timeboardedcode','timeboarded','day','timeperiodcode','timeperiod','routedescriptioncode','boardid','boardstopcode','boardstopname','boardlat','boardlong','alightid','alightstopcode','alightstopname','alightlat','alightlong']
columns_to_include=check_all_characters_present(new_df,columns_to_include_check)
# new_df[columns_to_include].to_csv('O2O_MUNI_Test.csv',index=False)
pprint(columns_to_include)
new_df=new_df[columns_to_include]

data_dictionary={'FIELD NAME': {0: 'ETC_ID',
  1: 'DATE',
  2: 'BOARD_TIMEPERIOD',
  3: 'BOARD_TIMEPERIOD',
  4: 'BOARD_TIMEPERIOD',
  5: 'BOARD_TIMEPERIOD',
  6: 'BOARD_TIMEPERIOD',
  7: 'BOARD_TIMEPERIOD',
  8: 'BOARD_TIMEPERIOD',
  9: 'BOARD_TIMEPERIOD',
  10: 'BOARD_TIMEPERIOD',
  11: 'BOARD_TIMEPERIOD',
  12: 'BOARD_TIMEPERIOD',
  13: 'BOARD_TIMEPERIOD',
  14: 'BOARD_TIMEPERIOD',
  15: 'BOARD_TIMEPERIOD',
  16: 'BOARD_TIMEPERIOD',
  17: 'BOARD_TIMEPERIOD',
  18: 'BOARD_TIMEPERIOD',
  19: 'TIME PERIOD',
  20: 'TIME PERIOD',
  21: 'TIME PERIOD',
  22: 'TIME PERIOD',
  23: 'TIME PERIOD',
  24: 'TIME PERIOD',
  25: 'TIME PERIOD',
  26: 'ROUTE_DESCRIPTION ',
  27: 'BOARD_STOP[Code]',
  28: 'BOARD_STOP_NAME',
  29: 'BOARD_LAT',
  30: 'BOARD_LON',
  31: 'ALIGHT_STOP[Code]',
  32: 'ALIGHT_STOP_NAME',
  33: 'ALIGHT_LAT',
  34: 'ALIGHT_LON'},
 'FIELD DESCRIPTION': {0: 'Unique record identifier',
  1: 'Date survey was completed',
  2: 'Timestamp when survey was initiated (Boarding)',
  3: 'Timestamp when survey was initiated (Boarding)',
  4: 'Timestamp when survey was initiated (Boarding)',
  5: 'Timestamp when survey was initiated (Boarding)',
  6: 'Timestamp when survey was initiated (Boarding)',
  7: 'Timestamp when survey was initiated (Boarding)',
  8: 'Timestamp when survey was initiated (Boarding)',
  9: 'Timestamp when survey was initiated (Boarding)',
  10: 'Timestamp when survey was initiated (Boarding)',
  11: 'Timestamp when survey was initiated (Boarding)',
  12: 'Timestamp when survey was initiated (Boarding)',
  13: 'Timestamp when survey was initiated (Boarding)',
  14: 'Timestamp when survey was initiated (Boarding)',
  15: 'Timestamp when survey was initiated (Boarding)',
  16: 'Timestamp when survey was initiated (Boarding)',
  17: 'Timestamp when survey was initiated (Boarding)',
  18: 'Timestamp when survey was initiated (Boarding)',
  19: 'Time Period when survey was initiated',
  20: 'Time Period when survey was initiated',
  21: 'Time Period when survey was initiated',
  22: 'Time Period when survey was initiated',
 23: 'Time Period when survey was initiated',
 24: 'Time Period when survey was initiated',
 25: 'Time Period when survey was initiated',
  26: 'Long Route name and Direction of Travel',
  27: 'ID of Stop respondent boarded at',
  28: 'Name of Stop respondent boarded at',
  29: 'Latitude of  Stop respondent boarded at',
  30: 'Longitude of  Stop respondent boarded at',
  31: 'ID of Stop respondent alighted at',
  32: 'Name of Stop respondent alighted at',
  33: 'Latitude of  Stop respondent alighted at',
  34: 'Longitude of  Stop respondent alighted at'},
 'FIELD VALUE': {0: 'Actual Value',
  1: 'Actual Value',
  2: 'AM1 = Before 6:00 am',
  3: 'AM2 = 6:00 am - 6:59 am',
  4: 'AM3 = 7:00 am - 7:59 am',
  5: 'AM4 = 8:00 am - 8:59 am',
  6: 'MID1 = 9:00 am - 9:59 am',
  7: 'MID2 = 10:00 am - 10:59 am',
  8: 'MID3 = 11:00 am - 11:59 am',
  9: 'MID4 = 12:00 pm - 12:59 pm',
  10: 'MID5 = 1:00 pm - 1:59 pm',
  11: 'MID6 = 2:00 pm - 2:59 pm',
  12: 'PM1 = 3:00 pm - 3:59 pm',
  13: 'PM2 = 4:00 pm - 4:59 pm',
  14: 'PM3 = 5:00 pm - 5:59 pm',
  15: 'PM4 = 6:00 pm - 6:59 pm',
  16: 'PM5 = 7:00 pm - 7:59 pm',
  17: 'PM6 = 8:00 pm - 8:59 pm',
  18: 'PM7 = After 9:00 pm',
 19: '0 = AM',
  20: '1 = MIDDAY',
  21: '2 = PM',
  22: '3 = PM PEAK',
  23: '4 = EVENING',
 24: '5 = NIGHT',
 25: '6 = OWL',
  26: 'Actual Value',
  27: 'Actual Value',
  28: 'Actual Value',
  29: 'Actual Value',
  30: 'Actual Value',
  31: 'Actual Value',
  32: 'Actual Value',
  33: 'Actual Value',
  34: 'Actual Value'}}

data_df=pd.DataFrame(data_dictionary)



# summary_df = new_df.groupby('TIME PERIOD[CODE]').apply(lambda x: x[['ROUTE_DESCRIPTION[CODE]', 'BOARD_STOP_NAME']])



with pd.ExcelWriter(f'O2O {project_name}.xlsx') as writer:
    new_df.to_excel(writer,sheet_name='O2O Data',index=False)
    data_df.to_excel(writer,sheet_name='data dictionary',index=False)
    # summary_df.to_excel(writer,sheet_name='summary')


print("File Generated Successfully")