import requests
import os


os.makedirs('books', exist_ok= True)
os.chdir('books')
for id in range(1, 11):
    url = f'https://tululu.org/txt.php?id={id}'
    response = requests.get(url)
    response.raise_for_status()
    if response.url == url:
        with open(f'text{id}.txt', 'wb') as file:
            file.write(response.content)

