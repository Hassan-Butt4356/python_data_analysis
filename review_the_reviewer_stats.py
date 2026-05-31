import pandas as pd
import numpy as np
from geopy.distance import geodesic
import warnings

warnings.filterwarnings('ignore')


# ke_df=pd.read_excel('COTA_KINGElvis.xlsx',sheet_name='Elvis_Review')
ke_df=pd.read_excel("COTA_KINGElvis.xlsx",sheet_name='Elvis_Review')
ke_df=ke_df[ke_df['INTERV_INIT']!=999]
ke_df=ke_df[ke_df['HAVE_5_MIN_FOR_SURVECode']==1]

df=pd.read_csv('elviscota2023obweekday_export_odbc.csv')

cota_df=pd.read_csv('cota2023obweekday_export_odbc.csv')

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
        pass

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

def review_the_reviewer(df,ke_df,cota_df):
    ke_df=ke_df[ke_df['INTERV_INIT']!=999]
    ke_df=ke_df[ke_df['INTERV_INIT']!='999']
    ke_df=ke_df[ke_df['HAVE_5_MIN_FOR_SURVECode']==1]
    # getting data from elvis database file which matches with KingElvis 
    df=pd.merge(df,ke_df[['id']],on='id',how='left',indicator=True)
    df['Matched'] = (df['_merge'] == 'both').astype(int)
    df.drop(columns=['_merge'])
    df=df[df['Matched']==1]
    df.drop_duplicates(subset=['id'],keep='first',inplace=True)

    # getting data from non-elvis database file which matches with KingElvis 
    cota_df=pd.merge(cota_df,ke_df[['id']],on='id',how='left',indicator=True)
    cota_df['Matched'] = (cota_df['_merge'] == 'both').astype(int)
    cota_df.drop(columns=['_merge'])
    cota_df=cota_df[cota_df['Matched']==1]
    cota_df.drop_duplicates(subset=['id'],keep='first',inplace=True)

    origin_home_columns_check=['originaddresslat', 'originaddresslong','originplacetype','homeaddresslat','homeaddresslong']
    origin_home_columns=check_all_characters_present(df,origin_home_columns_check)
    origin_home_columns.sort()
    origin_home_columns

    destin_home_columns_check=['destinaddresslat', 'destinaddresslong','destinplacetype','homeaddresslat','homeaddresslong']
    destin_home_columns=check_all_characters_present(df,destin_home_columns_check)
    destin_home_columns.sort()
    destin_home_columns
    # if origin lat/long not present in elvis database file then add home lat/long to those values
    for index, row in df.iterrows():
        if (pd.isna(row[origin_home_columns[2]]) or pd.isna(row[origin_home_columns[3]])) and 'home' in row[origin_home_columns[4]].lower():
            df.loc[index, origin_home_columns[2]] = row[origin_home_columns[0]]
            df.loc[index, origin_home_columns[3]] = row[origin_home_columns[1]]
            
        if (pd.isna(row[destin_home_columns[0]]) or pd.isna(row[destin_home_columns[1]])) and 'home' in str(row[destin_home_columns[2]]).lower():
            df.loc[index, destin_home_columns[0]] = row[destin_home_columns[3]]
            df.loc[index, destin_home_columns[1]] = row[destin_home_columns[4]]

    non_origin_home_columns_check=['originaddresslat', 'originaddresslong','originplacetype','homeaddresslat','homeaddresslong']
    non_origin_home_columns=check_all_characters_present(cota_df,non_origin_home_columns_check)
    non_origin_home_columns.sort()
    non_origin_home_columns

    non_destin_home_columns_check=['destinaddresslat', 'destinaddresslong','destinplacetype','homeaddresslat','homeaddresslong']
    non_destin_home_columns=check_all_characters_present(cota_df,non_destin_home_columns_check)
    non_destin_home_columns.sort()
    non_destin_home_columns

    # if origin lat/long not present in non elvis database file then add home lat/long to those values
    for index, row in cota_df.iterrows():
        if (pd.isna(row[non_origin_home_columns[2]]) or pd.isna(row[non_origin_home_columns[3]])) and ('home' in row[non_origin_home_columns[4]].lower()) :
            cota_df.loc[index, non_origin_home_columns[2]] = row[non_origin_home_columns[0]]
            cota_df.loc[index, non_origin_home_columns[3]] = row[non_origin_home_columns[1]]

        if (pd.isna(row[non_destin_home_columns[0]]) or pd.isna(row[non_destin_home_columns[1]])) and ('home' in str(row[non_destin_home_columns[2]]).lower()) :
            cota_df.loc[index, non_destin_home_columns[0]] = row[non_destin_home_columns[3]]
            cota_df.loc[index, non_destin_home_columns[1]] = row[non_destin_home_columns[4]]

    # get columns from elvis file
    origin_destin_prev_next_columns_check=['originaddresslat', 'originaddresslong', 'stoponlat', 'stoponlong', 'stopofflat', 'stopofflong','destinaddresslat', 'destinaddresslong','prevtransferscode','nexttransferscode']
    origin_destin_prev_next_columns=check_all_characters_present(df,origin_destin_prev_next_columns_check)
    origin_destin_prev_next_columns.sort()

    # get columns form non-elvis file
    non_origin_destin_prev_next_columns_check=['originaddresslat', 'originaddresslong', 'stoponlat', 'stoponlong', 'stopofflat', 'stopofflong','destinaddresslat', 'destinaddresslong','prevtransferscode','nexttransferscode']
    non_origin_destin_prev_next_columns=check_all_characters_present(cota_df,non_origin_destin_prev_next_columns_check)
    non_origin_destin_prev_next_columns.sort()

    # add elvis database columns in KINGElvis file and rename them to KE_ColumnsName
    ke_df=pd.merge(ke_df,df[['id',*origin_destin_prev_next_columns]],on='id',how='left')
    # ke_df=pd.merge(ke_df,df[['id',*origin_destin_prev_next_columns]],on='id',how='left')
    ke_df.rename(columns={'DESTIN_ADDRESS_LAT':'KE_DESTIN_ADDRESS_LAT','DESTIN_ADDRESS_LONG':'KE_DESTIN_ADDRESS_LONG',
                        'ORIGIN_ADDRESS_LAT':'KE_ORIGIN_ADDRESS_LAT','ORIGIN_ADDRESS_LONG':'KE_ORIGIN_ADDRESS_LONG',
                        'STOP_OFF_LAT':'KE_STOP_OFF_LAT','STOP_OFF_LONG':'KE_STOP_OFF_LONG','STOP_ON_LAT':'KE_STOP_ON_LAT',
                        'STOP_ON_LONG':'KE_STOP_ON_LONG','PREV_TRANSFERSCode':'KE_PREV_TRANSFERSCode','NEXT_TRANSFERSCode':'KE_NEXT_TRANSFERSCode'
                        },inplace=True)

    # add non-elvis database columns in KINGElvis file and rename them to KE_ColumnsName
    ke_df=pd.merge(ke_df,cota_df[['id',*non_origin_destin_prev_next_columns]],on='id',how='left')

    non_origin_destin_columns_check=['originaddresslat', 'originaddresslong','destinaddresslat', 'destinaddresslong']
    non_prev_next_columns_check=['prevtransferscode','nexttransferscode']
    non_origin_destin_columns=check_all_characters_present(cota_df,non_origin_destin_columns_check)
    non_prev_next_columns=check_all_characters_present(cota_df,non_prev_next_columns_check)
    non_origin_destin_columns.sort()
    non_prev_next_columns.sort()
    non_origin_destin_columns

    ke_df[[*non_prev_next_columns,'KE_PREV_TRANSFERSCode','KE_NEXT_TRANSFERSCode']]=ke_df[[*non_prev_next_columns,'KE_PREV_TRANSFERSCode','KE_NEXT_TRANSFERSCode']].fillna(0)


    ke_df[[*non_origin_destin_columns,'KE_ORIGIN_ADDRESS_LAT','KE_ORIGIN_ADDRESS_LONG','KE_DESTIN_ADDRESS_LAT','KE_DESTIN_ADDRESS_LONG']]=ke_df[[*non_origin_destin_columns,'KE_ORIGIN_ADDRESS_LAT','KE_ORIGIN_ADDRESS_LONG','KE_DESTIN_ADDRESS_LAT','KE_DESTIN_ADDRESS_LONG']].fillna(0)

    for index, row in ke_df.iterrows():
        num_changes = 0
        elvis_origin_lat=row['KE_ORIGIN_ADDRESS_LAT']
        elvis_origin_long=row['KE_ORIGIN_ADDRESS_LONG']
        non_elvis_origin_lat=row[non_origin_destin_columns[2]]
        non_elvis_origin_long=row[non_origin_destin_columns[3]]
        
        elvis_destin_lat=row['KE_DESTIN_ADDRESS_LAT']
        elvis_destin_long=row['KE_DESTIN_ADDRESS_LONG']
        non_elvis_destin_lat=row[non_origin_destin_columns[0]]
        non_elvis_destin_long=row[non_origin_destin_columns[1]]
        
        if all([elvis_origin_lat, elvis_origin_long, non_elvis_origin_lat, non_elvis_origin_long]):
            distance=get_distance_between_coordinates(elvis_origin_lat,elvis_origin_long,non_elvis_origin_lat,non_elvis_origin_long)
            ke_df.loc[index,'Origin Distance']=distance
            if distance > 0.15:
                ke_df.loc[index,'Origin Change']=1
                num_changes += 1
            else:
                ke_df.loc[index,'Origin Change']=0
        elif elvis_origin_lat and elvis_origin_long:
            ke_df.loc[index,'Origin Distance']=0
            num_changes += 1
            ke_df.loc[index,'Origin Change']=1
        elif non_elvis_origin_lat and non_elvis_origin_long:
            ke_df.loc[index,'Origin Distance']=0
            num_changes += 1
            ke_df.loc[index,'Origin Change']=1
        else:
            ke_df.loc[index,'Origin Distance']=0
            ke_df.loc[index,'Origin Change']=0
                

        if all([elvis_destin_lat, elvis_destin_long, non_elvis_destin_lat, non_elvis_destin_long]):
            distance=get_distance_between_coordinates(elvis_destin_lat,elvis_destin_long,non_elvis_destin_lat,non_elvis_destin_long)
            ke_df.loc[index,'Destin Distance']=distance
            if distance > 0.15:
                ke_df.loc[index,'Destin Change']=1
                num_changes += 1
            else:
                ke_df.loc[index,'Destin Change']=0
        elif elvis_destin_lat and elvis_destin_long:
            ke_df.loc[index,'Destin Distance']=0
            ke_df.loc[index,'Destin Change']=1
            num_changes += 1
        elif non_elvis_destin_lat and non_elvis_destin_long:
            ke_df.loc[index,'Destin Distance']=0
            ke_df.loc[index,'Destin Change']=1
            num_changes += 1
        else:
            ke_df.loc[index,'Destin Distance']=0
            ke_df.loc[index,'Destin Change']=0

        if row[non_prev_next_columns[0]] == row['KE_NEXT_TRANSFERSCode']:
            ke_df.loc[index,'NextTrans Change']=0
        else:
            ke_df.loc[index,'NextTrans Change']=1
            num_changes += 1

        if row[non_prev_next_columns[1]] == row['KE_PREV_TRANSFERSCode']:
            ke_df.loc[index,'PrevTrans Change']=0

        else:
            ke_df.loc[index,'PrevTrans Change']=1
            num_changes += 1

        ke_df.at[index, 'Change Count'] = num_changes



    ke_df['Low Count'] = np.where(ke_df['Change Count'] <= 1, 'Yes', 'No')


    stop_on_off_columns_check=['stoponlat', 'stoponlong', 'stopofflat', 'stopofflong']
    stop_on_off_columns=check_all_characters_present(ke_df,stop_on_off_columns_check)
    stop_on_off_columns.sort()


    ke_df[[*stop_on_off_columns,'KE_STOP_OFF_LAT', 'KE_STOP_OFF_LONG', 'KE_STOP_ON_LAT', 'KE_STOP_ON_LONG']]=ke_df[[*stop_on_off_columns,'KE_STOP_OFF_LAT', 'KE_STOP_OFF_LONG', 'KE_STOP_ON_LAT', 'KE_STOP_ON_LONG']].fillna(0)

    ke_stop_on_off_column_check=['kestopofflat','kestopofflong','kestoponlat','kestoponlong']
    ke_stop_on_off_column=check_all_characters_present(ke_df,ke_stop_on_off_column_check)
    ke_stop_on_off_column.sort()

    for index, row in ke_df.iterrows():
        if (
            (round(row[stop_on_off_columns[0]], 3) == round(row[ke_stop_on_off_column[0]], 3)) and
            (round(row[stop_on_off_columns[1]], 3) == round(row[ke_stop_on_off_column[1]], 3))
        ) and (
            (round(row[stop_on_off_columns[2]], 3) == round(row[ke_stop_on_off_column[2]], 3)) and
            (round(row[stop_on_off_columns[3]], 3) == round(row[ke_stop_on_off_column[3]], 3))
        ):
            ke_df.loc[index, 'Route Changes'] = 0
        else:
            ke_df.loc[index, 'Route Changes'] = 1
    
    return ke_df

ke_df=review_the_reviewer(df,ke_df,cota_df)

ke_df.to_csv("Review The Reviewer(Update)(01).csv",index=True)

#Summary Sheet Logic Here 

def route_level_information(ke_df):
    summary_df=pd.DataFrame()

    route_surveyed_column_check=['routesurveyedcode']
    route_surveyed_column=check_all_characters_present(ke_df,route_surveyed_column_check)

    def route_splited(value):
        return '_'.join(value.split('_')[:-1])

    ke_df['ROUTE_SURVEYEDCode_Splited']=ke_df[route_surveyed_column[0]].apply(route_splited)

    route_surveyed_column_splited_check=['routesurveyedcodesplited']
    route_surveyed_column_splited=check_all_characters_present(ke_df,route_surveyed_column_splited_check)
    route_surveyed_column_splited

    route_values=ke_df[route_surveyed_column_splited[0]].unique()
    summary_df['Route'] = route_values

    for index, row in summary_df.iterrows():
        overall_reviews=ke_df.shape[0]
        
        route_surveyed_value = row['Route']  # Assuming 'Route' is the correct column name in summary_df
        review_filter_condition = (
            (ke_df[route_surveyed_column_splited[0]] == route_surveyed_value) &
            ((ke_df['Final_Usage'].str.lower() == 'use') | (ke_df['Final_Usage'].str.lower() == 'remove'))
        )
        total_reviews = ke_df[review_filter_condition].shape[0]  # Adjust as needed
        removal_filter_condition = (
            (ke_df[route_surveyed_column_splited[0]] == route_surveyed_value) &
            (ke_df['Final_Usage'].str.lower() == 'remove')
        )
        total_removals = ke_df[removal_filter_condition].shape[0]
        removal_survey_ids_filter_condition=(
            (ke_df[route_surveyed_column_splited[0]]==route_surveyed_value)&
            (ke_df['Final_Usage'].str.lower()=='remove')
        )
        sum_of_origin_change_filter=(
                (ke_df[route_surveyed_column_splited[0]]==route_surveyed_value)&
                (ke_df['Origin Change']==1)
        )
        sum_of_destin_change_filter=(
                (ke_df[route_surveyed_column_splited[0]]==route_surveyed_value)&
                (ke_df['Destin Change']==1)
        )
        
        sum_of_prev_change_filter=(
                (ke_df[route_surveyed_column_splited[0]]==route_surveyed_value)&
                (ke_df['PrevTrans Change']==1)
        )
        
        sum_of_next_change_filter=(
                (ke_df[route_surveyed_column_splited[0]]==route_surveyed_value)&
                (ke_df['NextTrans Change']==1)
        )
        sum_of_record_change_filter=(
                (ke_df[route_surveyed_column_splited[0]]==route_surveyed_value)&
                (ke_df['Change Count']!=0)
        )
        removal_survey_ids=ke_df['id'][removal_survey_ids_filter_condition].values
        summary_df.loc[index, 'Total_Reviews'] = total_reviews
        summary_df.loc[index, 'Total_Removals'] = total_removals
        sum_origin_change=ke_df[sum_of_origin_change_filter].shape[0]
        sum_destin_change=ke_df[sum_of_destin_change_filter].shape[0]
        sum_nexttrans_change=ke_df[sum_of_next_change_filter].shape[0]
        sum_prevtrans_change=ke_df[sum_of_prev_change_filter].shape[0]
        sum_record_change=ke_df[sum_of_record_change_filter].shape[0]
        if total_reviews:
            summary_df.loc[index,'Removal_Rate_Percentage']=(total_removals*100)/total_reviews
        else:
            summary_df.loc[index,'Removal_Rate_Percentage']=0
        if overall_reviews:
            summary_df.loc[index,'Route_Reviewed_Percentage']=(total_reviews*100)/overall_reviews
        else:
            summary_df.loc[index,'Route_Reviewed_Percentage']=0
        summary_df.loc[index, 'Removed_Survey_ids'] = ', '.join(map(str, removal_survey_ids))
        summary_df.loc[index,'Sum of Origin Change']=sum_origin_change
        summary_df.loc[index,'Sum of Destin Change']=sum_destin_change
        summary_df.loc[index,'Sum of NextTrans Change']=sum_nexttrans_change
        summary_df.loc[index,'Sum of PrevTrans Change']=sum_prevtrans_change
        summary_df.loc[index,'Sum of Record Change']=sum_record_change
        summary_df.loc[index,'Origin Change Percentage']=f"{round((sum_origin_change*100)/total_reviews,2)}%"
        summary_df.loc[index,'Destin Change Percentage']=f"{round((sum_destin_change*100)/total_reviews,2)}%"
        summary_df.loc[index,'NextTrans Change Percentage']=f"{round((sum_nexttrans_change*100)/total_reviews,2)}%"
        summary_df.loc[index,'PrevTrans Change Percentage']=f"{round((sum_prevtrans_change*100)/total_reviews,2)}%"
        summary_df.loc[index,'Record Change Percentage']=f"{round((sum_record_change*100)/total_reviews,2)}%"

    return summary_df
    
summary_df=route_level_information(ke_df)

summary_df.to_csv('COTA_Reviewer_Summary.csv',index=False)

print('Files Generated Successfully')

# ke_df=pd.merge(ke_df,df[['id',route_surveyed_column[0]]],on='id',how='left')
# ke_df.rename(columns={'ROUTE_SURVEYEDCode_y':'ROUTE_SURVEYEDCode'},inplace=True)
# # Drop Test Records
# ke_df = ke_df[(ke_df['INTERV_INIT'] != '999') & (ke_df['INTERV_INIT'] != 999)]
# ke_df = ke_df[(ke_df['HAVE_5_MIN_FOR_SURVECode'] == 1)]

# # Is there a reviewer making a ton of changes
# reviewers_names = {}

# for index, row in ke_df[ke_df['FINAL_REVIEWER'].notna()].iterrows():
#     names = [name.strip() for name in row['FINAL_REVIEWER'].replace('.', ',').split(',')]
#     for name in names:
#         reviewers_names[name] = reviewers_names.get(name, 0) + 1

# print(max(reviewers_names,key=reviewers_names.get))

# print(reviewers_names)

# # Is there a reviewer not making any changes and we're getting a lot of our flags on their records to review again
# reviewers_flags = {}
# total_recovered=0
# for index, row in ke_df[(ke_df['FINAL_REVIEWER'].notna()) &(ke_df['Final_Usage']=='Use')].iterrows():
#     names = [name.strip() for name in row['FINAL_REVIEWER'].replace('.', ',').split(',')]
#     if len(names)>1:
# #         for name in names:
#         reviewers_flags[names[0]] = reviewers_flags.get(names[0], 0) + 1
#         total_recovered+=1

# print(max(reviewers_flags,key=reviewers_flags.get))

# print(reviewers_flags)


# #  Is there a certain route that is getting a lot of changes
# route_flags = {}

# for index, row in ke_df[(ke_df['FINAL_REVIEWER'].notna()) &(ke_df['Final_Usage']=='Use')].iterrows():
#     names = [name.strip() for name in row['FINAL_REVIEWER'].replace('.', ',').split(',')]
#     if len(names)>1:
#         route = '_'.join(row[route_surveyed_column[0]].split('_')[:-1])
#         route_flags[route] = route_flags.get(route, 0) + 1


# print(max(route_flags,key=route_flags.get))

# print(route_flags)

# # Overall summary (Previous transfers-20% are being changed)
# total_removed=0

# for index, row in ke_df[(ke_df['FINAL_REVIEWER'].notna()) &(ke_df['Final_Usage']=='Remove')].iterrows():
#     total_removed+=1
        
# print(f'{total_removed=}')
# print(f'{total_recovered=}')
# print(f'{(total_recovered * 100) / (total_recovered + total_removed)}%')

# overall_summary=f'{round((total_recovered * 100) / (total_recovered + total_removed),2)}%'
# overall_summary

# df_reviewer_flags = pd.DataFrame(list(reviewers_flags.items()), columns=['Reviewer_Name', 'Flagged Records'])
# df_route_flags = pd.DataFrame(list(route_flags.items()), columns=['Route_Flaged', 'Count'])
# df_reviewers_names = pd.DataFrame(list(reviewers_names.items()), columns=['Reviewer_Name', 'Records Reviewed'])

# summary_df = pd.DataFrame({
#     'Total_Recovered': [total_recovered],
#     'Total_Removed': [total_removed],
#     'Overall_Summary': [overall_summary]
# })

# result_df = pd.concat([df_reviewer_flags, df_route_flags, df_reviewers_names,summary_df], axis=1)

# result_df.to_csv("Review The Reviewer Stats.csv",index=False)