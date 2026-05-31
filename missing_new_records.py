import pandas as pd

import warnings

warnings.filterwarnings("ignore")

# Create old_df
# old_data = {
#     'elvis_id': [1, 2, 3, 4, 6, 9, 10, 13, 15],
#     'data': ['A', 'B', 'C', 'D', 'F', 'I', 'J', 'M', 'O']
# }
# old_ke = pd.DataFrame(old_data)

# # Create new_df
# new_data = {
#     'elvis_id': [5, 7, 8, 11, 12, 14, 16, 17, 18],
#     'data': ['E', 'G', 'H', 'K', 'L', 'N', 'P', 'Q', 'R']
# }
# new_ke = pd.DataFrame(new_data)


project='Tucson'

# old_ke=pd.read_excel('SEATTLE_WA_KINGElvis.xlsx',sheet_name='Elvis_Review')
# new_ke=pd.read_csv('SEATTLE_KINGElvis_no_aa.csv')

new_ke=pd.read_csv('elvistucson2025obweekday_export_odbc.csv')
old_ke=pd.read_csv('elvistucson2025obweekday_export_odbc_old.csv')


# new_df=pd.merge(new_ke, old_ke, on='elvis_id', how='left', indicator=True)
# new_df=pd.merge(new_ke, old_ke, on='id', how='left', indicator=True)

# filtered_df = new_df[new_df['_merge'] == 'left_only']
# filtered_df = filtered_df.drop(columns=['_merge'])

# filtered_df.to_csv(f"{project}_Missing_New_Records.csv",index=False)


# Merge the dataframes
new_df = pd.merge(new_ke, old_ke, on='id', how='left', indicator=True, suffixes=('', '_old'))

# Filter rows where the record is only in the left dataframe (new_ke)
filtered_df = new_df[new_df['_merge'] == 'left_only']

# Drop the '_merge' column
filtered_df = filtered_df.drop(columns=['_merge'])

# Save the filtered dataframe to a CSV file
filtered_df.to_csv(f"{project}_Missing_New_Records.csv", index=False)

# Merging the two DataFrames
# new_df = pd.merge(new_ke, old_ke['elvis_id'], on='elvis_id', how='left', indicator=True)

# # Filtering the data to keep only the new records
# filtered_df = new_df[new_df['_merge'] == 'left_only'].drop(columns=['_merge'])

# # Saving the filtered DataFrame to a CSV file
# filtered_df.to_csv("Missing_New_Records.csv", index=False)

print("File Created Successfully")
