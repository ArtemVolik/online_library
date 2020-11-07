import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename



def get_title(id):
    url = f'https://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()
    if response.url == url:
        soup = BeautifulSoup(response.text, features="lxml")
        title = soup.find('h1').text
        title = title.split('::')[0].strip()
        author = soup.find('h1').find('a').text.strip()
        return {'title': title, 'author': author}
    return



def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    if response.url == url:
        with open(filepath, 'wb') as file:
            file.write(response.content)


for book_id in range(1, 10):
    try:
        title = get_title(book_id)['title']
    except TypeError:
        continue
    url = f'https://tululu.org/txt.php?id={book_id}'
    download_txt(url, title, folder='books/')



