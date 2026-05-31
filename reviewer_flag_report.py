import pandas as pd
import numpy as np

import warnings

warnings.filterwarnings('ignore')

kingelvis_files=['EMBARK_OK_KINGElvis','SEATTLE_WA_KINGElvis','BART_CA_KINGElvis','PALMTRAN_FL_KINGElvis','MUNI_CA_KINGElvis']

latest_combined_flags=['reviewtool_20240722_SEATTLE_combinedflags']

# with pd.ExcelWriter('Overall_Review_Flag_Report.xlsx') as writer:
#     for file in kingelvis_files:
#         project = file.split('_')[0]
#         df = pd.read_excel(f"{file}.xlsx", sheet_name='Elvis_Review')
#         total_records = df.shape[0]
#         flag_condition = df['2X_REVIEW_CHECK'] == 1
#         total_flags = df[flag_condition].shape[0]
#         record_condition = df['1st Cleaner'].str.lower() == 'hereapi'
#         actual_records = df[record_condition].shape[0]
#         test_records = df[~record_condition].shape[0]
#         new_df = pd.DataFrame({
#             'Total_Survey_Records': [total_records],
#             'Actual_Records': [actual_records],
#             'Test_Records': [test_records],
#             'Total_Flags': [total_flags]
#         })
#         new_df.to_excel(writer, sheet_name=f'{project}_Report', index=False)


with pd.ExcelWriter('Overall_Review_Flag_Report.xlsx') as writer:
    for file in kingelvis_files:
        project = file.split('_')[0]
        df = pd.read_excel(f"{file}.xlsx", sheet_name='Elvis_Review')

        total_recheck_flags = 0  # Initialize to 0 before checking

        for idx, flag in enumerate(latest_combined_flags):
            if project.lower() in flag.lower():
                print(f"Yes, {project} is present at index {idx}")
                comb_df = pd.read_csv(f'{latest_combined_flags[idx]}.csv')
                comb_df.rename(columns={'2X_REVIEW_CHECK': "2X_REVIEW_RECHECK"}, inplace=True)
                df = pd.merge(df, comb_df[['elvis_id', '2X_REVIEW_RECHECK']], on='elvis_id', how='left')
                recheck_flag_condition = df['2X_REVIEW_RECHECK'] == 1
                total_recheck_flags = df[recheck_flag_condition].shape[0]
                break  # Exit the loop after finding the first match

        total_records = df.shape[0]
        flag_condition = df['2X_REVIEW_CHECK'] == 1
        total_flags = df[flag_condition].shape[0]
        record_condition = df['1st Cleaner'].str.lower() == 'hereapi'
        actual_records = df[record_condition].shape[0]
        test_records = df[~record_condition].shape[0]

        new_df = pd.DataFrame({
            'Total_Survey_Records': [total_records],
            'Actual_Records': [actual_records],
            'Test_Records': [test_records],
            'Total_Flags': [total_flags],
            'Total_Recheck_Flags': [total_recheck_flags]
        })

        new_df.to_excel(writer, sheet_name=f'{project}_Report', index=False)


# with pd.ExcelWriter('Reviewer_Review_Flag_Report.xlsx') as writer:
#     for file in kingelvis_files:
#         project = file.split('_')[0]
#         df = pd.read_excel(f"{file}.xlsx", sheet_name='Elvis_Review')
        
#         # Filter the actual records
#         actual_records = df[df['1st Cleaner'].str.lower() == 'hereapi']
        
#         # Get the unique reviewers
#         unique_reviewers = actual_records['FINAL_REVIEWER'].str.lower().unique()
        
#         # Initialize a list to hold the data
#         data = []

#         for reviewer in unique_reviewers:
#             reviewed_count = actual_records[actual_records['FINAL_REVIEWER'].str.lower() == reviewer].shape[0]
#             flagged_count = actual_records[(actual_records['FINAL_REVIEWER'].str.lower() == reviewer) & (actual_records['2X_REVIEW_CHECK'] == 1)].shape[0]
            
#             # Append the data to the list
#             data.append({
#                 'Reviewer Name': reviewer,
#                 'Records_Reviewed': reviewed_count,
#                 'Flag_Records': flagged_count
#             })
        
#         # Create a DataFrame from the list
#         new_df = pd.DataFrame(data)
        
#         # Write the DataFrame to the Excel file
#         new_df.to_excel(writer, sheet_name=f'{project}_Reviewer_Report', index=False)

with pd.ExcelWriter('Reviewer_Review_Flag_Report.xlsx') as writer:
    for file in kingelvis_files:
        project = file.split('_')[0]
        df = pd.read_excel(f"{file}.xlsx", sheet_name='Elvis_Review')
        
        # Filter the actual records
        actual_records = df[df['1st Cleaner'].str.lower() == 'hereapi']
        
        # Get the unique reviewers
        unique_reviewers = actual_records['FINAL_REVIEWER'].str.lower().unique()
        
        # Initialize a list to hold the data
        data = []

        # Initialize total_recheck_flags to 0
        total_recheck_flags = 0
        
        for idx, flag in enumerate(latest_combined_flags):
            if project.lower() in flag.lower():
                print(f"Yes, {project} is present at index {idx}")
                comb_df = pd.read_csv(f'{latest_combined_flags[idx]}.csv')
                comb_df.rename(columns={'2X_REVIEW_CHECK': "2X_REVIEW_RECHECK"}, inplace=True)
                actual_records = pd.merge(actual_records, comb_df[['elvis_id', '2X_REVIEW_RECHECK']], on='elvis_id', how='left')
                break  # Exit the loop after finding the first match

        for reviewer in unique_reviewers:
            reviewed_count = actual_records[actual_records['FINAL_REVIEWER'].str.lower() == reviewer].shape[0]
            flagged_count = actual_records[(actual_records['FINAL_REVIEWER'].str.lower() == reviewer) & (actual_records['2X_REVIEW_CHECK'] == 1)].shape[0]
            
            if '2X_REVIEW_RECHECK' in actual_records.columns:
                recheck_flagged_count = actual_records[(actual_records['FINAL_REVIEWER'].str.lower() == reviewer) & (actual_records['2X_REVIEW_RECHECK'] == 1)].shape[0]
            else:
                recheck_flagged_count = 0

            # Append the data to the list
            data.append({
                'Reviewer Name': reviewer,
                'Records_Reviewed': reviewed_count,
                'Flag_Records': flagged_count,
                'Recheck_Flag_Records': recheck_flagged_count
            })
        
        # Create a DataFrame from the list
        new_df = pd.DataFrame(data)
        
        # Write the DataFrame to the Excel file
        new_df.to_excel(writer, sheet_name=f'{project}_Reviewer_Report', index=False)