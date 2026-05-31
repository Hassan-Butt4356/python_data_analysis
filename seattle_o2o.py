import pandas as pd
import numpy as np
from datetime import datetime,date
import warnings
import copy

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
    return s.replace(':', '').replace('-', '').replace(')', '').replace('_', '').replace('[', '').replace(']', '').replace(' ','').replace('#','').lower()

today_date = date.today()
today_date=''.join(str(today_date).split('-'))
project_name='SEATTLE'

o2o_data_dict=pd.read_excel('O2O VTA.xlsx',sheet_name='data dictionary')

df=pd.read_csv('seattle_rail2024o2o_export_odbc.csv')

# Details File O2O_STOPS Sheet
detail_df=pd.read_excel('details_project_od_Seattle2 (1).xlsx',sheet_name='O2O_STOPS')

# Details File Stops Sheet
seq_df=pd.read_excel('details_project_od_Seattle2 (1).xlsx',sheet_name='STOPS')

code_columns=check_all_code_columns(df,df.columns)

code_columns=check_all_characters_present(df,code_columns)
columns_to_remove=[]
for column in code_columns:
    cleaned_column=clean_string(column)
#     if 'routesurveyed' in cleaned_column or 'language' in cleaned_column:
    if 'time' in cleaned_column or 'language' in cleaned_column:
        columns_to_remove.append(column)

o2o_df=copy.deepcopy(df)

new_df=o2o_df.drop(columns=columns_to_remove)

code_columns_check=check_all_characters_present(new_df,code_columns)

new_code_columns=check_all_characters_present(new_df,code_columns_check)

route_surveyed_column_check=['routesurveyed']
route_surveyed_column=check_all_characters_present(new_df,route_surveyed_column_check)

# to get the Line Value for database file using route_surveyed
def get_route_line(x):
    b_values=str(x).split('(')
    if len(b_values)>1:
        join_value=" ".join(b_values[:-1]).strip()
        values=str(join_value).split(' ')
        return values[-2]
    else:
        values=str(x).split(' ')
        if len(values)>1:
            return values[-2]
        return x
    
new_df['Line_Value']=new_df[route_surveyed_column[0]].apply(get_route_line)

# to get line value for details file using ETC_ROUTE_ID
def get_detail_route_line(x):
    values=str(x).split('_')
    if len(values)>1:
        return values[-2][0]
    else:
        return x
    
detail_df['Line_Value']=detail_df['ETC_ROUTE_ID'].apply(get_detail_route_line)

for _,row in new_df.iterrows():
    counter=0
    for i in range(1,len(new_code_columns)):
        value=row[code_columns[i]]

        if not pd.isnull(value):
            stop_value=value
            matched_value=detail_df[(detail_df['Line_Value']==row['Line_Value'])&(detail_df['STOP_ID']==value)]
            if not matched_value.empty:
                counter+=1
                if counter==1:
                    new_df.loc[row.name, ['ROUTE_DESCRIPTION[CODE]','ETC_ROUTE_NAME','BOARD_ID', 'BOARD_STOP[CODE]', 'BOARD_STOP_NAME']] = [
                        matched_value.iloc[0]['ETC_ROUTE_ID'], 
                        matched_value.iloc[0]['ETC_ROUTE_NAME'], 
                        matched_value.iloc[0]['STOP_ID'], 
                        matched_value.iloc[0]['ETC_STOP_ID'], 
                        matched_value.iloc[0]['ETC_STOP_NAME'], 
                        ]
                if counter>1:
                    new_df.loc[row.name, ['ALIGHT_ID', 'ALIGHT_STOP[CODE]', 'ALIGHT_STOP_NAME']] = [matched_value.iloc[0]['STOP_ID'], 
                        matched_value.iloc[0]['ETC_STOP_ID'], 
                        matched_value.iloc[0]['ETC_STOP_NAME']]

new_df['SEQ_CHECK'] = new_df['ALIGHT_ID'] - new_df['BOARD_ID']

ids_list = []
for _, row in new_df.iterrows():
    if row['SEQ_CHECK'] < 0:
        # Extract route code and modify it
        ids_list.append(row['id'])

        route_code = row['ROUTE_DESCRIPTION[CODE]']
        new_route_code = f"{'_'.join(route_code.split('_')[:-1])}_01" if route_code.split('_')[-1] == '00' else f"{'_'.join(route_code.split('_')[:-1])}_00"
        
        # Get new route name
        new_route_name_row = seq_df[seq_df['ETC_ROUTE_ID'] == new_route_code]
        if not new_route_name_row.empty:
            new_route_name = new_route_name_row['ETC_ROUTE_NAME'].iloc[0]
        else:
            # Handle the case when the new route name is not found
            continue  # Skip to the next iteration if new route code is not valid

        # Board stop details
        board_stop_row = seq_df[(seq_df['ETC_ROUTE_ID'] == new_route_code) & (seq_df['ETC_STOP_NAME'] == row['BOARD_STOP_NAME'])]
        if not board_stop_row.empty:
            board_stop_code = board_stop_row['ETC_STOP_ID'].iloc[0]
            board_stop_lat_lon = board_stop_row[['seq_fixed', 'stop_lat6', 'stop_lon6']].iloc[0]
        else:
            # Skip if no board stop information is found
            continue

        # Alight stop details
        alight_stop_row = seq_df[(seq_df['ETC_ROUTE_ID'] == new_route_code) & (seq_df['ETC_STOP_NAME'] == row['ALIGHT_STOP_NAME'])]
        if not alight_stop_row.empty:
            alight_stop_code = alight_stop_row['ETC_STOP_ID'].iloc[0]
            alight_stop_lat_lon = alight_stop_row[['seq_fixed', 'stop_lat6', 'stop_lon6']].iloc[0]
        else:
            # Skip if no alight stop information is found
            continue

        # Update new_df with the retrieved values
        new_df.loc[row.name, 'ROUTE_DESCRIPTION[CODE]'] = new_route_code
        new_df.loc[row.name, 'ETC_ROUTE_NAME'] = new_route_name

        new_df.loc[row.name, 'Board_Seq'] = board_stop_lat_lon['seq_fixed']
        new_df.loc[row.name, 'BOARD_STOP[CODE]'] = board_stop_code

        new_df.loc[row.name, 'BOARD_STOP_ON_LAT'] = board_stop_lat_lon['stop_lat6']
        new_df.loc[row.name, 'BOARD_STOP_ON_LONG'] = board_stop_lat_lon['stop_lon6']

        new_df.loc[row.name, 'Alight_Seq'] = alight_stop_lat_lon['seq_fixed']
        new_df.loc[row.name, 'ALIGHT_STOP[CODE]'] = alight_stop_code

        new_df.loc[row.name, 'ALIGHT_STOP_ON_LAT'] = alight_stop_lat_lon['stop_lat6']
        new_df.loc[row.name, 'ALIGHT_STOP_ON_LONG'] = alight_stop_lat_lon['stop_lon6']


new_df=pd.merge(new_df,df[['id','TIME_BOARDED_Code_']],on='id',how='left')


new_df['Date'] = np.where(new_df['Completed'].notna(), new_df['Completed'], new_df['Date_started'])

def get_day_name(x):
    if pd.isna(x):
        return np.nan
    x = str(x)
    try:
        date_object = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            date_object = datetime.strptime(x, '%d/%m/%Y %H:%M')
        except ValueError:
            return np.nan
    day_name = date_object.strftime('%A')
    if day_name in ['Saturday', 'Sunday']:
        return 'Weekend'
    return 'Weekday'

new_df['Day']=new_df['Date'].apply(get_day_name)

new_df=new_df[new_df['INTERV_INIT']!='999']

new_df.dropna(subset=['ROUTE_DESCRIPTION[CODE]','BOARD_ID', 'BOARD_STOP[CODE]', 'BOARD_STOP_NAME','ALIGHT_ID', 'ALIGHT_STOP[CODE]', 'ALIGHT_STOP_NAME'],inplace=True)


time_period_mapping = {
    'PM1': 'PM',
    'PM2': 'Evening',
    'MID': 'MIDDAY',
    'AM': 'AM'
}

time_period_code_mapping = {
    'PM':2,
    'Evening':4,
    'MIDDAY':1,
    'AM': 0
}

new_df['TIME PERIOD'] = new_df['TIME_BOARDED_Code_'].map(time_period_mapping).fillna(new_df['TIME_BOARDED_Code_'])
new_df['TIME PERIOD[Code]'] = new_df['TIME PERIOD'].map(time_period_code_mapping)

# To get seq from detials file 
# for _, row in new_df.iterrows():
#     # Extract the alight sequence
#     alight_seq_df = seq_df[(seq_df['ETC_ROUTE_NAME'] == row['ETC_ROUTE_NAME']) & 
#                            (seq_df['ETC_STOP_NAME'] == row['ALIGHT_STOP_NAME'])][['seq_fixed']]
#     if not alight_seq_df.empty:
#         alight_seq = alight_seq_df.iloc[0, 0]
#     else:
#         alight_seq = 0
    
#     # Extract the board sequence
#     board_seq_df = seq_df[(seq_df['ETC_ROUTE_NAME'] == row['ETC_ROUTE_NAME']) & 
#                           (seq_df['ETC_STOP_NAME'] == row['BOARD_STOP_NAME'])][['seq_fixed']]
#     if not board_seq_df.empty:
#         board_seq = board_seq_df.iloc[0, 0]
#     else:
#         board_seq = 0

#     # Assign values to new_df
#     new_df.loc[row.name, 'Alight_Seq'] = alight_seq
#     new_df.loc[row.name, 'Board_Seq'] = board_seq

# new_df['SEQ_CHECK'] = new_df['Alight_Seq'] - new_df['Board_Seq']

# To drop records where SEQ_CHECK is 0
# new_df = new_df[new_df['SEQ_CHECK'] != 0].copy()

# for _, row in new_df.iterrows():
#     if row['SEQ_CHECK'] < 0:
#         # Swap the board and alight values
#         board_id = row['BOARD_ID']
#         board_stop_code = row['BOARD_STOP[CODE]']
#         board_stop_name = row['BOARD_STOP_NAME']
#         alight_id = row['ALIGHT_ID']
#         alight_stop_code = row['ALIGHT_STOP[CODE]']
#         alight_stop_name = row['ALIGHT_STOP_NAME']

#         new_df.loc[row.name, 'BOARD_ID'] = alight_id
#         new_df.loc[row.name, 'BOARD_STOP[CODE]'] = alight_stop_code
#         new_df.loc[row.name, 'BOARD_STOP_NAME'] = alight_stop_name
#         new_df.loc[row.name, 'ALIGHT_ID'] = board_id
#         new_df.loc[row.name, 'ALIGHT_STOP[CODE]'] = board_stop_code
#         new_df.loc[row.name, 'ALIGHT_STOP_NAME'] = board_stop_name

with open('RouteChangesIDS.txt','w') as f:
    for item in ids_list:
        f.write(f"{item}\n")

final_df=new_df[['id','Date','Day','TIME_BOARDED_Code_','TIME_BOARDED','TIME PERIOD','TIME PERIOD[Code]','Line_Value','ROUTE_DESCRIPTION[CODE]','ETC_ROUTE_NAME','BOARD_STOP[CODE]','BOARD_ID' ,'BOARD_STOP_NAME','ALIGHT_STOP[CODE]','ALIGHT_ID','ALIGHT_STOP_NAME']]
# new_df[['id','Date','Day','TIME_BOARDED_Code_','TIME_BOARDED','TIME PERIOD','TIME PERIOD[Code]','ROUTE_DESCRIPTION[CODE]','ETC_ROUTE_NAME','Line_Value','BOARD_ID', 'BOARD_STOP[CODE]', 'BOARD_STOP_NAME','ALIGHT_ID', 'ALIGHT_STOP[CODE]', 'ALIGHT_STOP_NAME']].to_csv('SEATTLE_O2O_Old_Logic.csv',index=False)
with pd.ExcelWriter(f'O2O_{today_date}_{project_name}_rail.xlsx') as writer:
    final_df.to_excel(writer,sheet_name='O2O Data',index=False)
    o2o_data_dict.to_excel(writer,sheet_name='data dictionary',index=False)


print("FILE CREATED SuccessFully")