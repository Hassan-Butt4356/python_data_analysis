import pandas as pd
import numpy as np
from datetime import datetime,date
import warnings
import copy

warnings.filterwarnings('ignore')

project_name='SEATTLE'

file_name='SEATTLE_WA_KINGElvis.xlsx'

elvis_df=pd.read_excel(file_name,sheet_name='Elvis_Review')

elvis_df=elvis_df.query("`1st Cleaner` == 'HereAPI'")
removed_df=elvis_df.query('Final_Usage=="Remove"')

filtered_df = removed_df[removed_df['SUPERVISOR_COMMENT'].notna() & (removed_df['SUPERVISOR_COMMENT'] != '')]


filtered_df[['Elvis_Date','elvis_id','1st Cleaner','SUPERVISOR_COMMENT','FINAL_REVIEWER']]

filtered_df.to_csv(f'{project_name}_Supervisor_Comment_Review.csv',index=False)

print('FILE GENERATED SUCCESSFULLY')