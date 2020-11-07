import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def get_title(id):
    url = f'https://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()

    if response.url == url:

        soup = BeautifulSoup(response.text, features="lxml")
        title = soup.find('h1').text
        title = title.split('::')[0].strip()
        print(title)
        print()
        # author = soup.find('h1').find('a').text.strip()
        cover_image_href = soup.find('div', class_='bookimage').find('img')['src']
        cover_image_url = urljoin('https://tululu.org/', cover_image_href)
        comments_site = soup.find_all('div', class_='texts')
        for raw_comment in comments_site:
            comment = raw_comment.text.split(')')[-1]
            print(comment)
        return title, cover_image_url






def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    if response.url == url:
        with open(filepath, 'wb') as file:
            file.write(response.content)


def download_image(url, filename,  folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, filename)
    print(os.path.splitext(filename))
    print(filepath)
    if response.url == url:
        with open(filepath, 'wb') as file:
            file.write(response.content)


for book_id in range(1, 11):
    get_title(book_id)

# for book_id in range(1, 10):
#
#     try:
#         title, url = get_title(book_id)
#
#     except TypeError:
#         continue



   # download_image(url, url.split('/')[-1], folder='images/')
    # download_txt(url, title, folder='books/')




