from bs4 import BeautifulSoup
import requests
import pandas as pd
from numbers import Number
import os
import boto3
from io import StringIO

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_DEFAULT_REGION')
)

url = 'https://en.wikipedia.org/wiki/List_of_multiple_Olympic_medalists'
headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find_all('table')[0]
titles = table.find_all('th')
table_titles = [title.text.strip() for title in titles]
df = pd.DataFrame(columns=table_titles)

rows = table.find_all('tr')[1:]
previous_values = []
for row in rows:
    cols = row.find_all('td')
    cols = [col.text.strip() for col in cols]
    if len(cols) == 9:
        cols.insert(0, previous_values[0])
        cols.append(previous_values[10])
    elif len(cols) == 10:
        if isinstance(previous_values[0], Number) or previous_values[0].isdigit():
            cols.append(previous_values[10])
        else:
            cols.insert(0, previous_values[0])
    if len(cols) == len(table_titles):
        length = len(df)
        df.loc[length] = cols
        previous_values = cols

print(df)

# Upload to S3
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)

bucket_name = 's3bucketforwebscraper'
file_name = 'olympic_medalists.csv'

s3_client.put_object(
    Bucket=bucket_name,
    Key=file_name,
    Body=csv_buffer.getvalue()
)

print(f"File uploaded successfully to s3://{bucket_name}/{file_name}")