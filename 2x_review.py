import pandas as pd
import numpy as np

import warnings

warnings.filterwarnings('ignore')

file_name = 'COTA_KINGElvis (3).xlsx'

old_combine_df=pd.read_excel(file_name,sheet_name='Elvis_Review')

new_combine_df=pd.read_csv("Merged Checks.csv")

old_combine_df=old_combine_df[old_combine_df['1st Cleaner']!='Test/No 5 MIN']
new_combine_df=new_combine_df[new_combine_df['1st Cleaner']!='Test/No 5 MIN']


if old_combine_df.shape[0] > new_combine_df.shape[0]:
    old_combine_df = pd.merge(old_combine_df, new_combine_df[['id']], on='id', how='inner')


elif old_combine_df.shape[0] < new_combine_df.shape[0]:
    new_combine_df = pd.merge(new_combine_df, old_combine_df[['id']], on='id', how='inner')
    
old_combine_df.drop_duplicates(subset=['id'],inplace=True)
new_combine_df.drop_duplicates(subset=['id'],inplace=True)
# 'else' case is not needed as you are not performing any operation

# If you want to drop the '_merge' and 'Available IDs' columns (if present)
old_combine_df.drop(columns=['_merge'], inplace=True, errors='ignore')
new_combine_df.drop(columns=['_merge'], inplace=True, errors='ignore')

old_combine_df = old_combine_df.sort_values(by='id')
new_combine_df = new_combine_df.sort_values(by='id')

old_combine_df.reset_index(inplace=True)
new_combine_df.reset_index(inplace=True)

old_combine_df.drop(columns=['2x_REVIEWED_FLAG'],inplace=True)

for index, row in old_combine_df.iterrows():
    old_value = row['2X_REVIEW_CHECK']
    new_value = new_combine_df.loc[index, '2X_REVIEW_CHECK']
    if old_value != new_value:
        new_combine_df.at[index, '2x_REVIEWED_FLAG'] = new_value
    else:
        new_combine_df.at[index, '2x_REVIEWED_FLAG'] = old_value


new_combine_df.to_csv("2x_KINGElvis_Review.csv",index=False)