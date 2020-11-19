import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse
import json
from tqdm import tqdm
import time


class UrlRedirectError(Exception):
    def __str__(self):
        return "Website redirect requested URl"

def is_response_ok(url, response):
    try:
        if url != response.url:
            raise UrlRedirectError
        response.raise_for_status()
    except requests.exceptions.HTTPError as er:
        print(url, ' - ', er)
        return
    except UrlRedirectError as er:
        print(er,' - ', url)
        return
    except ConnectionError as er:
        print('Connection Error')
        time.sleep(10)
        return
    return True



def write_to_json(json_path, books_description):
    with open(json_path, 'a', encoding='utf8') as file:
        json.dump(books_description, file, ensure_ascii=False)


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
        if not is_response_ok(url, response):
            continue
        soup = BeautifulSoup(response.content, features='lxml')

        all_books = soup.find_all('table', class_='d_book')
        for book in all_books:
            book = book.find('a')['href']
            books_urls.append(urljoin(url, book))
    return books_urls


def get_book_info(book_url, books_description, skip_image, skip_txt, images_folder, text_folder):
    """Return book description, save text and image.

    Function parse book webpage save picture and
    Invoke in it's body download_txt() and download_image() which
    save image and text version of the book.
    """
    url = book_url
    response = requests.get(url)
    response.raise_for_status()

    if not is_response_ok(url, response):
        return
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

    book_link = soup.select_one('table.d_book a[title$=txt]')
    if book_link:
        book_url_href = book_link['href']
    book_path = None
    if not skip_txt and book_link:
        book_txt_download_url = urljoin(url, book_url_href)
        book_path = download_txt(book_txt_download_url, book_title, text_folder)

    books_description.append ({'title': book_title,
                                 'author': book_author,
                                 'image_src': image_path,
                                 'book_path': book_path,
                                 'comments': book_comments,
                                 'genres': genres})


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    if not is_response_ok(url, response):
        return
    with open(filepath, 'wb') as file:
        file.write(response.content)
        return filepath


def download_image(url, filename, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, filename)
    if not is_response_ok(url, response):
        return
    with open(filepath, 'wb') as file:
        file.write(response.content)
        return filepath


if __name__ == '__main__':

    args = get_command_line_parameters()
    images_folder = 'images/'
    text_folder = 'books/'
    book_json_path = 'books_info.json'
    books_description = []
    if args.json_path:
        book_json_path = os.path.join(args.json_path, book_json_path)
    if args.dest_folder:
        images_folder = os.path.join(args.dest_folder, images_folder)
        text_folder = os.path.join(args.dest_folder, text_folder)
    if args.dest_folder and not args.json_path:
        book_json_path = os.path.join(args.dest_folder, book_json_path)

    get_books_urls(start_page=args.start_page, end_page=args.end_page)

    pbar = tqdm(get_books_urls(start_page=args.start_page, end_page=args.end_page))
    print('Parsing book data')
    for book_url in pbar:
        try:
            get_book_info(book_url, books_description, skip_image=args.skip_images, skip_txt=args.skip_txt,
                          images_folder=images_folder, text_folder=text_folder)
        except (requests.exceptions.HTTPError, UrlRedirectError) as er:
            print(er)
            continue
        except ConnectionError as er:
            print(er)
            time.sleep(10)
            continue
    write_to_json(book_json_path, books_description)
