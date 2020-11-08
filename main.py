import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import json
import re
import argparse

def parametrs_handler():
    parser = argparse.ArgumentParser('Parsing books for own library')
    parser.add_argument('--start_page', default=1, type=int, help="Enter page number to start")
    parser.add_argument('--end_page', default=701, type=int, help='Enter page number to stop')
    parser.add_argument('--dest_folder', type=str, default=0, help='Enter parser destination folder')
    parser.add_argument('--skip_images', action='store_true')
    parser.add_argument('--skip_txt', action='store_true')
    parser.add_argument('--json_path', type=str, default=0)
    args = parser.parse_args()
    return args


def get_books_urls(category_url='https://tululu.org/l55/'):
    start, stop = args.start_page, args.end_page
    books_urls = []
    for page in range(start, stop+1):
        url = category_url
        if page > 1:
            url = f'{url}{page}/'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, features='lxml')

        # не разобрался как селектом заменить, подскажите
        all_books = soup.find_all('table', class_='d_book')
        for book in all_books:
            book = book.find('a')['href']
            scheme, path = urlparse(category_url)[0:2]
            books_urls.append(urljoin(f'{scheme}://{path}', book))
            # if len(books_urls) == 35:
        return books_urls


def get_book_info(book):
    url = book
    response = requests.get(url)
    response.raise_for_status()
    if response.url == url:
        soup = BeautifulSoup(response.text, features="lxml")

        book_title = soup.select_one('h1').text
        book_title = book_title.split('::')[0].strip()

        author_selector = 'h1 a'
        book_author = soup.select_one(author_selector).text.strip()

        image_selector = ' .bookimage img'
        image_src = soup.select_one(image_selector)['src']

        scheme, path = urlparse(url)[0:2]
        image_url = urljoin(f'{scheme}://{path}', image_src)
        image_extension = image_src.split('/')[2]
        image_path = download_image(image_url, image_extension, folder='images/')

        book_comments_selector = '.texts > .black'
        book_comments = soup.select(book_comments_selector)
        book_comments = [comment.text for comment in book_comments]

        genres_selector = 'span.d_book a'
        genres = soup.select(genres_selector)
        genres = [genre.text for genre in genres]

        print('перед писком ссылки', url)
        print(soup.find('table', class_='d_book'))
        try:
            # не понял как селектом заменить, подскажите
            book_url_href = soup.find('table', class_='d_book').find('a', title=re.compile(r'txt'))['href']
            print(url)
        except BaseException:
            print("Текст книги отсутсвует")
            return
        print('хреф', book_url_href)
        book_txt_download_url = urljoin(f'{scheme}://{path}', book_url_href)
        print('урл', book_txt_download_url)

        book_path = download_txt(book_txt_download_url, book_title, folder='books/')


        books_info.append({
            'title': book_title,
            'author': book_author,
            'image_src': image_path,
            'book_path': book_path,
            'comments': book_comments,
            'genres': genres
        })

        with open('books_info.json', 'w', encoding='utf8') as file:
            json.dump(books_info, file, ensure_ascii=False)


def download_txt(url, filename, folder='books/'):
    if args.skip_txt:
        return
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    if response.url == url:
        with open(filepath, 'wb') as file:
            file.write(response.content)
            return filepath


def download_image(url, filename, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, filename)
    if response.url == url:
        with open(filepath, 'wb') as file:
            file.write(response.content)
            return filepath


if __name__ == '__main__':
    args = parametrs_handler()
    print(len(get_books_urls()))
    print(get_books_urls())
    books_info = []
    for book_url in get_books_urls():
        print("переходим к поштучному скачиванию")
        get_book_info(book_url)
