from database import DatabaseConnector
import pandas as pd
import copy
from decouple import config
from utils import  (
    check_routes, 
    check_stops,
    preprocess_for_Final_Reviewer,
    check_home_airport_hotel
)
from constants import (
    columns_names,
    columns_check_lat_lng,
    final_results_columns,
    columns_to_check_for_kingelvis
)
from pprint import pprint
from datetime import datetime
from helper import (
    details_dataframe,
    check_all_characters_present,
)
import warnings
import pprint
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    HOST = config("HOST")
    USER = config("USER")
    PASSWORD = config("PASSWORD")  # No need to quote_plus
    DATABASE = config("DATABASE")
    # DATABASE = "cotaoh2023"
    print("DB=>",DATABASE)
    # api_key = config("API_KEY")

    db_connector = DatabaseConnector(HOST, 'databasename', USER, PASSWORD)


    db_connector.connect()  # Connect to the database

    connection = db_connector.connection  # Get the MySQL connection object
    

    # for loading details file to check airport data

    name_KE = "BART"
    select_query = "SELECT * FROM database"
    filename='details_project_od_excel_UTA.xlsx'

    # Check if the CSV file exists
    csv_filename = select_query.split(" ")[-1]+".csv"
    df = pd.read_sql(select_query, connection)
    # print(pd.read_sql(select_query, connection))
    # print(df)
    # df.to_csv("lacmta2023obweekday_export_odbc(new).csv", index=False)
    try:
        df = pd.read_csv(csv_filename)
        print(f"FILE ALREADY EXISTS WITH THIS NAME: {csv_filename}")
    except FileNotFoundError:
        # File doesn't exist, read from the database and save to CSV    
        # df = pd.read_sql(select_query, connection)
        print(df.head(2))
        df.to_csv(csv_filename, index=False)  # Save the DataFrame to CSV
    # Close the database connection
    # db_connector.disconnect()

    exit()
    # old_df=pd.read_csv('KingElvis(lacmta)_AA.csv')
    # latest_elvis_date = old_df['Elvis_Date'].max()  

    # df['Date_last_action'] = pd.to_datetime(df['Date_last_action'])

    # Filter the df DataFrame to get rows where Date_last_action is greater than or equal to the latest Elvis date
    # df = df[df['Date_last_action'] >= latest_elvis_date]

    # df = df[df['id'] > 7577]
    df1=df[df['INTERV_INIT']!='999']

    additional_columns = ['ROUTE_STATUS', 'Stops_Status', 'Test_Status'] #ToDo: UpperCase these column names

    if all(col_name in df.columns for col_name in additional_columns):
        df.drop(columns=additional_columns,inplace=True)

    # for loading details file to check airport data
    # filename='details_project_od_excel_UTA.xlsx'
    details_df=details_dataframe(filename)

    df1=check_home_airport_hotel(df1,details_df)

    # To delete all Origin and Destin lat lng values if not present
    columns_to_check_origin_destin_lat_lng =check_all_characters_present(df1,columns_check_lat_lng)

    columns_to_include = check_all_characters_present(df1,columns_names)  # Initialize an empty list


    df1=df1.dropna(subset=columns_to_check_origin_destin_lat_lng)
    
    if all(col_name in df1.columns for col_name in additional_columns):
        for col in additional_columns:
            columns_to_include.append(col)
    
    route_df=df1.loc[:,columns_to_include]
    
    # routes_df = check_routes(route_df)
    routes_df=copy.deepcopy(route_df)
    route_df['ROUTE_STATUS']='Elvis_Review'

    #  Write the Routes Status
    # routes_df.to_csv("Routes and Stops Approval(lacmta).csv",index=False)

    # stops_df=route_df.drop(columns=['id'])

    # stops_list_data=stops_df.values.tolist()

    # data=check_stops(stops_list_data)
    # route_df['Stops_Status']=data['stops']
    # route_df['Test_Status']=data['tested']
    route_df['Stops_Status']='Elvis_Review'
    route_df['Test_Status']='TESTED'
    # Write the Stops Status
    # route_df.to_csv("Routes and Stops Approval(hrtva).csv",index=False)
    # pprint("Routes and Stops Approval(lacmta).csv  File generated Successfully")
    final_results =df.merge(route_df[['id', 'ROUTE_STATUS', 'Stops_Status','Test_Status']], on='id', how='left')
    
    if 'ROUTE_STATUS' in final_results.columns:
        final_results['ROUTE_STATUS'].fillna('Elvis_Review', inplace=True)
    if 'Stops_Status' in final_results.columns:
        final_results['Stops_Status'].fillna('Elvis_Review', inplace=True)
    if 'Test_Status' in final_results.columns:
        final_results['Test_Status'].fillna('Tested', inplace=True)
    # final_results.to_csv("ELVIS_lacmta_TEST.csv",index=False)
    # For KingElvis File Generation
    # columns_to_check = check_all_characters_present(final_results,columns_to_check_for_kingelvis)
    # final_results.dropna(subset=columns_to_check,how='any',inplace=True)
    current_date = datetime.now().date()
    final_columns_to_include= check_all_characters_present(final_results,final_results_columns)
    final_test=final_results[final_columns_to_include]
    data=preprocess_for_Final_Reviewer(final_test)
    final_test.insert(0, 'Elvis_Date', current_date)
    final_test.insert(1,'SUPERVISOR_COMMENT',final_test['ELVIS_COMMENT'])
    # final_test.insert(1,'distance_flag',' ')
    final_test.insert(1,'distance_flag',final_test['Stops_Status'])
    # final_test.insert(1,'route_match_flag',' ')
    final_test.insert(1, 'route_match_flag', final_test['ROUTE_STATUS'])
    final_test.insert(1,'REASON FOR REMOVAL [Other]',' ')
    final_test.insert(1,'REASON FOR REMOVAL',' ')
    # final_test.insert(1,'2x_FINAL_Review',data['final_review'])
    missing_values = len(final_test) - len(data['final_reviewer'])
    data['final_reviewer'].extend([pd.NA] * missing_values)
    final_test.insert(1, 'FINAL_REVIEWER', data['final_reviewer'])
    final_test.insert(1, 'Final_Usage', data['final_usage'])
    final_test.insert(1, '2nd Cleaner', ' ')
    final_test.insert(1, '1st Cleaner', data['first_cleaner'])
    final_test.insert(1, 'elvis_id', final_test['id'])

    # final_test=pd.concat([old_df,final_test],axis=0,ignore_index=True)

    final_test.to_csv(f'{name_KE}_KINGElvis.csv',index=False)
    print(f'{name_KE}_KINGElvis.csv  GENERATED SUCCESSFULLY')