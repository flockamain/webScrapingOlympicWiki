from bs4 import BeautifulSoup
import requests
import pandas as pd
from numbers import Number
import os

url = 'https://en.wikipedia.org/wiki/List_of_multiple_Olympic_medalists'
headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

## getting the table headers
table = soup.find_all('table')[0]
titles = table.find_all('th')
table_titles = [title.text.strip() for title in titles]
df = pd.DataFrame(columns=table_titles)
print(df)

## getting the table rows
rows = table.find_all('tr')[1:]  # Skip the header row
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

# Save to local file system (Docker container)
output_dir = '/app/output'  # Mount this as a volume in Docker
os.makedirs(output_dir, exist_ok=True)

file_name = 'olympic_medalists.csv'
output_path = os.path.join(output_dir, file_name)
df.to_csv(output_path, index=False)

print(f"File saved successfully to {output_path}")