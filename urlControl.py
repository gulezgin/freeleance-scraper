import pandas as pd
import requests


excel_path = ''  # Excel dosya yolunu buraya ekleyin
df = pd.read_excel(excel_path)

# URL'leri kontrol et 
for index, row in df.iterrows():
    url = row['URLs']
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f'{url}: Success')
        else:
            print(f'{url}: Fail (Status code: {response.status_code})')
    except requests.exceptions.RequestException as e:
        print(f'{url}: Fail ({e})')