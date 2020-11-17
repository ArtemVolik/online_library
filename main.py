import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import json
import argparse
from tqdm import tqdm
import time
import sys

class UrlRedirectError(Exception):
    print("Website redirect requested URl")


def write_to_json(json_path, book_title, book_author, image_path, book_path, book_comments, genres):
    book_description = {
        'title': book_title,
        'author': book_author,
        'image_src': image_path,
        'book_path': book_path,
        'comments': book_comments,
        'genres': genres
    }
    with open(json_path, 'a', encoding='utf8') as file:
        json.dump(book_description, file, ensure_ascii=False)


def get_command_line_parameters():
    parser = argparse.ArgumentParser('Parsing books for own library')
    parser.add_argument('--start_page', default=1, type=int, help="Enter page number to start")
    parser.add_argument('--end_page', default=701, type=int, help='Enter page number to stop')
    parser.add_argument('--dest_folder', type=str, help='Enter parsed data destination folder')
    parser.add_argument('--skip_images', action='store_true', help='If mentioned images download will be skipped')
    parser.add_argument('--skip_txt', action='store_true', help='If mentioned text files download will be skipped')
    parser.add_argument('--json_path', type=str, help='Enter .json file destination')
    args = parser.parse_args()
    return args


def get_books_urls(start_page, end_page, category_url='https://tululu.org/l55/'):
    """Get urls from category page.

    Args:
    start_page: number of start page
    end_page: number of end page
    category_url: category page url

    Returns:
    list: urls list of books in mentioned category
    """

    books_urls = []
    print('Looking for book urls')
    for page in tqdm(range(start_page, end_page + 1)):
        url = category_url
        if page > 1:
            url = f'{url}{page}/'
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as er:
            print(er)
            continue
        except ConnectionError:
            time.sleep(10)
            continue
        soup = BeautifulSoup(response.content, features='lxml')

        # не разобрался как селектом заменить, подскажите
        # я по весь цикл, или зlесь не нужно?
        all_books = soup.find_all('table', class_='d_book')
        for book in all_books:
            book = book.find('a')['href']
            books_urls.append(urljoin(url, book))
    return books_urls


def get_book_info(book_url, skip_image, skip_txt, images_folder, text_folder, json_path):
    """Save book information, text and image.

    Function parse book webpage and save information to json file.
    Invoke in it's body download_txt() and download_image() which
    save image and text version of the book.
    """
    url = book_url
    response = requests.get(url)
    response.raise_for_status()

    if not response.url == url:
        raise UrlRedirectError
    soup = BeautifulSoup(response.text, features="lxml")

    book_title = soup.select_one('h1').text
    book_title = book_title.split('::')[0].strip()

    author_selector = 'h1 a'
    book_author = soup.select_one(author_selector).text.strip()

    image_selector = ' .bookimage img'
    image_src = soup.select_one(image_selector)['src']
    image_url = urljoin(url, image_src)
    image_extension = image_src.split('/')[2]

    image_path = ''
    if not skip_image:
        image_path = download_image(image_url, image_extension, images_folder)

    book_comments_selector = '.texts > .black'
    book_comments = soup.select(book_comments_selector)
    book_comments = [comment.text for comment in book_comments]

    genres_selector = 'span.d_book a'
    genres = soup.select(genres_selector)
    genres = [genre.text for genre in genres]

    # спасибо за статью про реджексы в ЦСС, когда делал - не нашел.
    book_link = soup.select_one('table.d_book a[title$=txt]')

    # проверку чуть изменил, так как NoneType is not subscriptable
    # в любом случае сейчас доходит до конца и записыват ту инфу которая есть.
    # python main.py --start_page 28 --end_page 30 , на этих страницах нет ссылок на скачивание, для проверки
    if book_link:
        book_url_href = book_link['href']
    book_path = None
    if not skip_txt and book_link:
        book_txt_download_url = urljoin(url, book_url_href)
        book_path = download_txt(book_txt_download_url, book_title, text_folder)

    write_to_json(json_path, book_title, book_author, image_path, book_path, book_comments, genres)


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    if not response.url == url:
        raise UrlRedirectError
    with open(filepath, 'wb') as file:
        file.write(response.content)
        return filepath


def download_image(url, filename, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, filename)
    if not response.url == url:
        raise UrlRedirectError
    with open(filepath, 'wb') as file:
        file.write(response.content)
        return filepath


if __name__ == '__main__':

    args = get_command_line_parameters()
    images_folder = 'images/'
    text_folder = 'books/'
    book_json_path = 'books_info.json'

    if args.json_path:
        book_json_path = os.path.join(args.json_path, book_json_path)
    if args.dest_folder:
        images_folder = os.path.join(args.dest_folder, images_folder)
        text_folder = os.path.join(args.dest_folder, text_folder)
    if args.dest_folder and not args.json_path:
        book_json_path = os.path.join(args.dest_folder, book_json_path)

    pbar = tqdm(get_books_urls(start_page=args.start_page, end_page=args.end_page))
    print('Parsing book data')
    for book_url in pbar:
        try:
            get_book_info(book_url, skip_image=args.skip_images, skip_txt=args.skip_txt, images_folder=images_folder,
                          text_folder=text_folder, json_path=book_json_path)
        except requests.exceptions.HTTPError as er:
            print(er)
        except ConnectionError:
            time.sleep(10)
            continue
