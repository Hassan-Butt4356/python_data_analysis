import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

if __name__ == "__main__":
    name_KE='LAGUARDIA'
    df=pd.read_csv('elvislaguardia2024intercept_export_odbc(2).csv')

    # origin destin boarding alighting
    od_ba_names_check=['originaddresslat', 'originaddresslong', 'stoponlat', 'stoponlong', 'stopofflat', 'stopofflong', 'destinaddresslat', 'destinaddresslong']



    def check_all_characters_present(df, columns_to_check):
        # Function to clean a string by removing underscores and square brackets and converting to lowercase
        def clean_string(s):
            return s.replace('_', '').replace('[', '').replace(']', '').lower()

        # Clean and convert all column names in df to lowercase for case-insensitive comparison
        df_columns_lower = [clean_string(column) for column in df.columns]

        # Clean and convert the columns_to_check list to lowercase for case-insensitive comparison
        columns_to_check_lower = [clean_string(column) for column in columns_to_check]

        # Use a list comprehension to filter columns
        matching_columns = [column for column in df.columns if clean_string(column) in columns_to_check_lower]

        return matching_columns


    od_ba_names=check_all_characters_present(df,od_ba_names_check)
    od_ba_names.sort()

    missing_address_lat=40.77292364642215
    missing_address_long=-73.87219764178501

    def fill_missing_coordinates(row, missing_lat, missing_long, columns):
        for i in range(0, len(columns), 2):
            lat_col, long_col = columns[i], columns[i+1]
            if pd.isna(row[lat_col]) and pd.isna(row[long_col]):
                row[lat_col] = missing_lat
                row[long_col] = missing_long
        return row

    df=df.apply(fill_missing_coordinates, axis=1, 
                        missing_lat=missing_address_lat, 
                        missing_long=missing_address_long, 
                        columns=od_ba_names)
    df.to_csv('elvislaguardia2024intercept_export_odbc_filled.csv',index=False)
    print("Origin_Destin_Boarding_Alighting values filled and file generated Successfully")

    column_names=['id', 'originaddresslat', 'originaddresslong', 'prevtran1onbuslat', 'prevtran1onbuslong', 'prevtran1offbuslat', 'prevtran1offbuslong', 'prevtran2onbuslat', 'prevtran2onbuslong', 'prevtran2offbuslat', 'prevtran2offbuslong', 'prevtran3onbuslat', 'prevtran3onbuslong', 'prevtran3offbuslat', 'prevtran3offbuslong', 'prevtran4onbuslat', 'prevtran4onbuslong', 'prevtran4offbuslat', 'prevtran4offbuslong', 'stoponlat', 'stoponlong', 'stopofflat', 'stopofflong', 'nexttran1onbuslat', 'nexttran1onbuslong', 'nexttran1offbuslat', 'nexttran1offbuslong', 'nexttran2onbuslat', 'nexttran2onbuslong', 'nexttran2offbuslat', 'nexttran2offbuslong', 'nexttran3onbuslat', 'nexttran3onbuslong', 'nexttran3offbuslat', 'nexttran3offbuslong', 'nexttran4onbuslat', 'nexttran4onbuslong', 'nexttran4offbuslat', 'nexttran4offbuslong', 'destinaddresslat', 'destinaddresslong']

    columns_to_include = check_all_characters_present(df,column_names)


    final_results_columns=['id', 'completed', 'intervinit', 'routesurveyedcode', 'routesurveyed', 'have5minforsurvecode', 'have5minforsurve', 'origintransportcode', 'origintransport', 'originplacetype','destintransportcode', 'destintransport', 'destinplacetype', 'elvisstatus', 'elviscomment', 'intrvnote', 'routestatus', 'stopsstatus', 'teststatus']


    final_columns_to_include= check_all_characters_present(df,final_results_columns)

    final_test=df[final_columns_to_include]

    current_date = datetime.now().date()

    final_test.insert(0, 'Elvis_Date', current_date)
    final_test.insert(1,'SUPERVISOR_COMMENT',final_test['ELVIS_COMMENT'])
    final_test.insert(1,'route_match_flag','Elvis_Review')
    final_test.insert(1,'distance_flag','Elvis_Review')
    final_test.insert(1,'POSSIBLE ERRORS',' ')
    final_test.insert(1,'REASON FOR REMOVAL [Other]',' ')
    final_test.insert(1,'REASON FOR REMOVAL',' ')
    final_test.insert(1, 'FINAL_REVIEWER', ' ')
    final_test.insert(1, 'Final_Usage', ' ')
    final_test.insert(1, '2nd Cleaner', ' ')
    final_test.insert(1, '1st Cleaner', ' ')
    final_test.insert(1, 'elvis_id', final_test['id'])
    final_test.drop_duplicates(subset=['id'],keep='first',inplace=True)
    for _,row in final_test.iterrows():
        interv_init = row['INTERV_INIT']
        have_5_min = row['HAVE_5_MIN_FOR_SURVECode']
        if interv_init=='999':
            final_test.loc[row.name,'1st Cleaner']='Test'        
            final_test.loc[row.name,'FINAL_REVIEWER']='Test/No 5 MIN'
            final_test.loc[row.name,'Final_Usage']='Remove'
        elif have_5_min!=1:

            final_test.loc[row.name,'1st Cleaner']='No 5 MIN'        
            final_test.loc[row.name,'FINAL_REVIEWER']='Test/No 5 MIN'
            final_test.loc[row.name,'Final_Usage']='Remove'
        else:
            final_test.loc[row.name,'1st Cleaner']='HereAPI'        
            final_test.loc[row.name,'FINAL_REVIEWER']=' '
            final_test.loc[row.name,'Final_Usage']='Use'
            # final_test.loc[row.name,'Final_Usage']=' '
    # final_test[['Final_Usage']].fillna('Use',inplace=True)
    final_test['ROUTE_STATUS']='Elvis_Review'
    final_test['Stops_Status']='Elvis_Review'
    final_test['Test_Status']='Tested'
    final_test.to_csv(f'{name_KE}_KINGElvis_no_aa.csv',index=False)
    
    print(f'{name_KE}_KINGElvis created successfully')