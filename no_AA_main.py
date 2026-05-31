from database import DatabaseConnector
import pandas as pd
import numpy as np
from decouple import config
from utils import  (
    check_home_airport_hotel
)
from constants import (
    columns_names,
    columns_check_lat_lng,
    final_results_columns,

)
import copy
from datetime import datetime
from helper import (
    details_dataframe,
    check_all_characters_present,
)
import warnings

warnings.filterwarnings("ignore")


if __name__ == "__main__":
    HOST = config("HOST")
    USER = config("USER")
    PASSWORD = config("PASSWORD")  # No need to quote_plus
    DATABASE = config("DATABASE")

    # api_key = config("API_KEY")

    # db_connector = DatabaseConnector(HOST, DATABASE, USER, PASSWORD)
    # db_connector = DatabaseConnector(HOST, 'elvisbartca2024', USER, PASSWORD)
    # db_connector = DatabaseConnector(HOST, 'elvispalmtranod2024', USER, PASSWORD)
    # db_connector = DatabaseConnector(HOST, 'elvismunica2024', USER, PASSWORD)
    db_connector = DatabaseConnector(HOST, 'elvisdenverco2024', USER, PASSWORD)
    # db_connector = DatabaseConnector(HOST, 'elvisembarkok2024', USER, PASSWORD)
    # db_connector = DatabaseConnector(HOST, 'elvisseattleod2024', USER, PASSWORD)

    db_connector.connect()  # Connect to the database

    connection = db_connector.connection  # Get the MySQL connection object
    

    # for loading details file to check airport data
    # 43290
    # name_KE = "BART"
    # select_query = "SELECT * FROM elvisbartca2024interceptNEW_main_export_odbc"
    # filename='details_project_od_BART.xlsx'
    
    # name_KE = "EMBARK"
    # select_query = "SELECT * FROM elvisembark2024obweekday_export_odbc"
    # filename='details_project_od_excel_EMBARK.xlsx'

    # name_KE = "MUNI"
    # select_query = "SELECT * FROM elvismunica2024obweekday_export_odbc"
    # filename='details_project_od_MUNI.xlsx'

    # name_KE = "PALMTRAN"
    # select_query = "SELECT * FROM elvispalmtran2024obweekday_export_odbc"
    # filename='details_project_od_excel_PALMTRAN.xlsx'

# database = elvisdenverco2024


    name_KE = "DENVER"
    select_query = "select * from elvisdenverco2024obweekday_export_odbc"
    filename='details_project_od_excel_DENVER.xlsx'

    # name_KE = "SEATTLE"
    # select_query = "SELECT * FROM elvisseattlewa2024obweekday_export_odbc"
    # filename='details_project_od_Seattle.xlsx'

    # name_KE = "HRT"
    # select_query = "SELECT * FROM elvishrtva2023obweekday_export_odbc"
    # filename='details_hrta_va_od_excel.xlsx'

    # name_KE = "BCT"
    # select_query = "SELECT * FROM elvisbroward2023obweekday_export_odbc"
    # filename='details_project_od_excel_BCT.xlsx'
    
    # name_KE = "2023_GCRTA"
    # select_query = "SELECT * FROM elvisawsclevelandrta2023obweekday_export_odbc"
    # filename='details_2023_GCRTA_od_excel.xlsx'
    
    # name_KE = "LACMTA"
    # select_query = "SELECT * FROM elvislacmta2023obweekday_export_odbc"
    # filename='details_LACMTA_CA_excel.xlsx' 
    
    # name_KE = "WAKE_TRIANGLE"
    # select_query = "SELECT * FROM elviswakenc2023obweekday_export_odbc"
    # filename='details_project_od_excel_WakeTriangle.xlsx'
    
    # name_KE = "VICTOR_VALLEY"
    # select_query = "SELECT * FROM elvisvictorvalley2023obweekday_export_odbc"
    # filename='details_project_VICTOR_CA_excel.xlsx'

    # name_KE = "COTA"
    # select_query = "SELECT * FROM elviscota2023obweekday_export_odbc"
    # filename='details_project_od_excel_COTA.xlsx'

    # name_KE = "SANDAG"
    # select_query = "SELECT * FROM elvissandag2023obweekday_export_odbc"
    # filename='details_2022_SANDAG_CA_od_excel.xlsx'

    # name_KE = "COTA"
    # select_query = "SELECT * FROM elviscota2023obweekday_export_odbc"
    # filename='details_project_od_excel_COTA.xlsx'

    # name_KE = "SantaClarita"
    # select_query = "SELECT * FROM elvissantaclarita2023obweekday_export_odbc"
    # filename='details_project_od_SantaClarita.xlsx'
    
    # name_KE = "OKI"
    # select_query = "SELECT * FROM elviscincinnatioh2023obweekday_export_odbc"
    # filename='details_project_od_excel_OKI.xlsx'
    


    # Check if the CSV file exists
    csv_filename = select_query.split(" ")[-1]+".csv"

    try:
        df = pd.read_csv(csv_filename)
        print(f"FILE ALREADY EXISTS WITH THIS NAME: {csv_filename}")
    except FileNotFoundError:
        # File doesn't exist, read from the database and save to CSV
        df = pd.read_sql(select_query, connection)
        print(df.head(2))
        df.to_csv(csv_filename, index=False)  # Save the DataFrame to CSV
    # Close the database connection
    db_connector.disconnect()

    # exit()

    # old_df=pd.read_csv('KingElvis(lacmta)_AA.csv')
    # latest_elvis_date = old_df['Elvis_Date'].max()  

    # df['Date_last_action'] = pd.to_datetime(df['Date_last_action'])

    # Filter the df DataFrame to get rows where Date_last_action is greater than or equal to the latest Elvis date
    # df = df[df['Date_last_action'] >= latest_elvis_date]
    # df = df[df['id'] > 53890]
    # df1 = df[(df['INTERV_INIT'] != '999')] 
    # df1=df1[(df1['INTERV_INIT'] != 999)]
    # df1 = df1[(df1['HAVE_5_MIN_FOR_SURVECode'] == 1)]
    # df1=df[df['INTERV_INIT']!='999']
    df1=copy.deepcopy(df)
  
    details_df=details_dataframe(filename)

    df1=check_home_airport_hotel(df1,details_df)

    # To delete all Origin and Destin lat lng values if not present
    columns_to_check_origin_destin_lat_lng =check_all_characters_present(df1,columns_check_lat_lng)

    columns_to_include = check_all_characters_present(df1,columns_names)  # Initialize an empty list

    # Uncomment if you want to drop values where lat long is not available
    # df1=df1.dropna(subset=columns_to_check_origin_destin_lat_lng)
    
    # route_df.drop(columns=['id'],inplace=True)

    final_columns_to_include= check_all_characters_present(df1,final_results_columns)

    final_test=df1[final_columns_to_include]

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
            final_test.loc[row.name,'Final_Usage']=' '

    # final_test['Final_Usage'] = np.where(final_test['1st Cleaner'] == 'Test',
    # "Remove",
    # np.where(
    #     final_test['1st Cleaner'] == 'No 5 MIN',
    #     'Remove',
    #     " "
    # ))

    final_test['ROUTE_STATUS']='Elvis_Review'
    final_test['Stops_Status']='Elvis_Review'
    final_test['Test_Status']='Tested'
    final_test.to_csv(f'{name_KE}_KINGElvis_no_aa.csv',index=False)
    print(f'{name_KE}_KINGElvis created successfully')