from __future__ import print_function
import clicksend_client
from clicksend_client import SmsMessage
from clicksend_client.rest import ApiException
import os
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# Configure HTTP basic authorization
configuration = clicksend_client.Configuration()
configuration.username = 'USERNAME'  # replace with your ClickSend username
configuration.password = 'API_KEY'   # replace with your API key

# Create API client
api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))

df=pd.read_csv('stlouis2025obweekday_export_odbc.csv')
df1 = pd.read_csv('etc_research_8383_export_odbc.csv', header=0, skiprows=[1])

def check_all_characters_present(df, columns_to_check):
    """
    Returns the list of DataFrame columns that match any cleaned version
    of the columns in `columns_to_check`, using a custom cleaning rule.
    """
    # Define a helper function to clean column names
    def clean(s):
        return ''.join(c for c in s.lower() if c not in {'_', '[', ']', ' ', '#'})

    # Create a set of cleaned column names to check for faster lookup
    columns_to_check_cleaned = set(map(clean, columns_to_check))

    # Filter df columns that match the cleaned names
    matching_columns = [col for col in df.columns if clean(col) in columns_to_check_cleaned]

    return matching_columns

def format_us_phone_numbers(df, phone_column):
    """
    Adds '+1' prefix to US phone numbers in the specified phone column,
    only if the number is not already in international format.
    """
    def format_number(num):
        if pd.isna(num):
            return num
        # Convert to string if it's a float
        num_str = str(num).strip()
        
        # If it's already in the format with a plus sign, just return it
        if num_str.startswith('+'):
            return num_str
        
        # Remove any non-numeric characters (like spaces or dashes) before adding '+1'
        num_str = ''.join(filter(str.isdigit, num_str))
        
        # Add the country code if it's not already present
        return '+1' + num_str

    df[phone_column[0]] = df[phone_column[0]].apply(format_number)
    return df



phone_column_check=['followupsmsphone']
phone_column=check_all_characters_present(df,phone_column_check)
mainsid_column_check=['mainsid']
mainsid_column=check_all_characters_present(df1,mainsid_column_check)
response_column_check=['responseid']
response_column=check_all_characters_present(df1,response_column_check)

df= format_us_phone_numbers(df, phone_column)

new_df=df[df[phone_column[0]].notna()][['id',phone_column[0]]]
new_df[response_column[0]] = new_df['id'].astype(str)

merged_df = pd.merge(new_df, df1, left_on=response_column[0], right_on=response_column[0], how='left')

merged_df.drop_duplicates(subset=response_column[0],inplace=True)

survey_end_columns_check=['incentive01','incentive02','incentive03','end']
survey_end_columns=check_all_characters_present(merged_df,survey_end_columns_check)
survey_end_columns.sort()


survey_question_columns_check = [
    'q101', 'q102', 'q103', 'q104', 'q105', 'q201', 'q202', 'q203', 'q204', 'q205', 'q206', 'q207',
    'q3', 'q3a01', 'q3a02', 'q3a03', 'q3a04', 'q3a05', 'q3a06', 'q3a07',
    'q4', 'q4a01', 'q4a02', 'q4a03', 'q4a04', 'q4a05', 'q4a06', 'q4a07',
    'q501', 'q502', 'q503', 'q6', 'q6a01', 'q6a02', 'q6a03', 'q6a04', 'q6a05', 'q6a06', 'q6a07', 'q6a7',
    'q7', 'q801', 'q802', 'q803', 'q804', 'q805', 'q806', 'q807', 'q808', 'q809', 'q810',
    'q901', 'q902', 'q9x15', 'q1001', 'q1002', 'q10x8', 'q11'
]
survey_question_columns = check_all_characters_present(merged_df, survey_question_columns_check)
survey_question_columns.sort()


data_to_save = []
csv_filename = "survey_links_sent.csv"

# Read existing data from the CSV if it exists
if os.path.exists(csv_filename):
    df_existing = pd.read_csv(csv_filename)
else:
    # Create an empty DataFrame if the file does not exist
    df_existing = pd.DataFrame(columns=["Phone Number", "Response ID", "Main SID", "URL", "Status", "Count"])

# Iterate through the merged_df to process both existing and new records
for _, row in merged_df.iterrows():
    response_id = int(row[response_column[0]])
    print(response_id, type(response_id))
    phone_number = row[phone_column[0]]
    mainsid = row[mainsid_column[0]]

    # Skip if mainsid is missing or empty
    if pd.isna(mainsid) or str(mainsid).strip() == "":
        continue

    # Check if the response_id already exists in the CSV
    matching_row = df_existing[df_existing["Response ID"] == response_id]
    
    # If the response_id is found, process the existing record
    if not matching_row.empty:
        print('inside matching data')
        count = int(matching_row["Count"].iloc[0])  # Get the current count from the file
        
        # If the count is <= 2, proceed with the message sending logic
        if count <= 2:
            # 1. Survey completed?
            if any(pd.notna(row[col]) for col in survey_end_columns):
                status = "Completed"
                message_text = ""
            # 2. Partial survey?
            elif any(pd.notna(row[col]) for col in survey_question_columns):
                # Send RESUME LINK
                resume_url = f"https://etc-research.com/index.php/8383?lang=en&MAINSID={mainsid}&RESPONSEID={response_id}"
                message_text = f"Please complete this short follow-up survey: {resume_url}"
                status = "Partial - Resume Sent"
                count += 1
                
                # Send SMS
                sms_message = SmsMessage(source="python", body=message_text, to=str(phone_number))
                sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
                try:
                    api_response = api_instance.sms_send_post(sms_messages)
                    print(f"Sent to {phone_number}: {api_response}")
                except ApiException as e:
                    print(f"Failed to send to {phone_number}: {e}")
                    status = "Failed"
            # 3. Never started
            else:
                # Send full survey link
                full_url = f"https://etc-research.com/index.php/8383?lang=en&MAINSID={mainsid}&RESPONSEID={response_id}"
                message_text = f"Reminder to answer this short follow-up survey: {full_url}"
                status = "Not Started - Survey Link Sent"
                count += 1
                
                # Send SMS
                sms_message = SmsMessage(source="python", body=message_text, to=str(phone_number))
                sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
                try:
                    api_response = api_instance.sms_send_post(sms_messages)
                    print(f"Sent to {phone_number}: {api_response}")
                except ApiException as e:
                    print(f"Failed to send to {phone_number}: {e}")
                    status = "Failed"

            # Update the existing row in df_existing
            df_existing.loc[df_existing["Response ID"] == response_id, ["URL", "Status", "Count"]] = [message_text, status, count]
        else:
            print('Condition Not met')
    # If the response_id is not found, process as a new record
    else:
        print('not inside matching data')
        count = 0  # Start count at 0 for new records

        # 1. Survey completed?
        if any(pd.notna(row[col]) for col in survey_end_columns):
            status = "Completed"
            message_text = ""
        # 2. Partial survey?
        elif any(pd.notna(row[col]) for col in survey_question_columns):
            # Send RESUME LINK
            resume_url = f"https://etc-research.com/index.php/8383?lang=en&MAINSID={mainsid}&RESPONSEID={response_id}"
            message_text = f"Please complete this short follow-up survey: {resume_url}"
            status = "Partial - Resume Sent"
            count += 1
            
            # Send SMS
            sms_message = SmsMessage(source="python", body=message_text, to=str(phone_number))
            sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
            try:
                api_response = api_instance.sms_send_post(sms_messages)
                print(f"Sent to {phone_number}: {api_response}")
            except ApiException as e:
                print(f"Failed to send to {phone_number}: {e}")
                status = "Failed"
        # 3. Never started
        else:
            # Send full survey link
            full_url = f"https://etc-research.com/index.php/8383?lang=en&MAINSID={mainsid}&RESPONSEID={response_id}"
            message_text = f"Reminder to answer this short follow-up survey: {full_url}"
            status = "Not Started - Survey Link Sent"
            count += 1
            
            # Send SMS
            sms_message = SmsMessage(source="python", body=message_text, to=str(phone_number))
            sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
            try:
                api_response = api_instance.sms_send_post(sms_messages)
                print(f"Sent to {phone_number}: {api_response}")
            except ApiException as e:
                print(f"Failed to send to {phone_number}: {e}")
                status = "Failed"

        # Log info for new records
        data_to_save.append([phone_number, response_id, mainsid, message_text, status, count])

# Convert data_to_save to a DataFrame (only new records)
if data_to_save:
    df_to_save = pd.DataFrame(data_to_save, columns=["Phone Number", "Response ID", "Main SID", "URL", "Status", "Count"])
    
    # Combine existing data (updated in-place) with new data
    df_existing_updated = pd.concat([df_existing, df_to_save], ignore_index=True)
else:
    # If no new records, use the updated df_existing directly
    df_existing_updated = df_existing

# Write the updated data back to the CSV file
df_existing_updated.to_csv(csv_filename, index=False)