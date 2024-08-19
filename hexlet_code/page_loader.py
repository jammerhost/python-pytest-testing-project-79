import os.path
import string
from pathlib import Path
from urllib import parse

import requests
from bs4 import BeautifulSoup

# todo: использовать дата классы


DOWNLOADABLE_TAGS_WITH_SRC_ATTRS = {
    'img': 'src',
    'link': 'href',
    'script': 'src',
}


def get_tags_to_download():
    return DOWNLOADABLE_TAGS_WITH_SRC_ATTRS.keys()


def get_source_attr_for_tag(tag: str) -> str | None:
    return DOWNLOADABLE_TAGS_WITH_SRC_ATTRS.get(tag)


def make_path_by_url(url: str, keep_extension: bool = False) -> str:
    default_suffix = '.html'
    parsed_url = parse.urlparse(url)

    suffix = ''
    url_path = parsed_url.path
    if keep_extension:
        suffix = Path(url_path).suffix or default_suffix
        url_path = str(Path(url_path).with_suffix(''))

    url = f'{parsed_url.netloc}{url_path}'

    path = ''
    for s in url:
        if s not in string.ascii_letters + string.digits:
            path += '-'
        else:
            path += s

    return f'{path}{suffix}'


def ensure_absolute_url(url: str, domain_with_scheme: str) -> str:
    parsed_url = parse.urlparse(url)
    if not parsed_url.netloc:
        url = f'{domain_with_scheme}{url}'
    return url


def is_local_resource(url: str, domain_with_scheme: str) -> bool:
    """Определяем, является ли файл на странице локальным ресурсом, то есть расположенном на одном домене со страницей

    >>> is_local_resource('https://ru.hexlet.org/assets/python.png', 'https://ru.hexlet.org')
    True

    >>> is_local_resource('/assets/python.png', 'https://ru.hexlet.org')
    True

    >>> is_local_resource('https://cdn2.hexlet.io/assets/error-pages/404', 'https://ru.hexlet.org')
    False
    """
    parsed_url = parse.urlparse(url)
    parsed_domain = parse.urlparse(domain_with_scheme)
    if parsed_url.netloc and parsed_url.netloc != parsed_domain.netloc:
        return False
    return True


def handle_files_in_html(html_text: str, files_directory: str, domain_with_scheme: str) -> tuple[list[dict], str]:
    soup = BeautifulSoup(html_text, 'html.parser')
    result = []
    for resource in soup.find_all(get_tags_to_download()):
        src_attr = get_source_attr_for_tag(resource.name)
        if not src_attr:
            continue

        if not is_local_resource(resource[src_attr], domain_with_scheme):
            continue

        absolute_url = ensure_absolute_url(
            resource[src_attr], domain_with_scheme)
        downloaded_path = str(
            Path(files_directory) / make_path_by_url(absolute_url, keep_extension=True))

        result.append({
            'original_url': resource[src_attr],
            'downloaded_path': downloaded_path,
        })

        resource[src_attr] = downloaded_path

    return result, soup.prettify()


def download(url: str, directory: str) -> str:
    """

    Получить содержимое страницы по указанному URL
    Получить ссылки на ресурсы (картинки) из содержимого страницы и заменить их внутри страницы на путь к локальному файлу
    Скачать ресурсы в указанную директорию
    Сохранить страницу в указанную директорию
    """
    parsed_url = parse.urlparse(url)
    domain_with_scheme = f'{parsed_url.scheme}://{parsed_url.netloc}'
    response = requests.get(url)
    page_text = response.text

    path = make_path_by_url(url)
    files_directory = f'{path}_files'

    files, handled_page_text = handle_files_in_html(
        page_text, files_directory, domain_with_scheme)

    if files and not os.path.exists(Path(directory) / files_directory):
        os.mkdir(Path(directory) / files_directory)

    for file in files:
        file_url = ensure_absolute_url(
            file['original_url'], domain_with_scheme)
        file_path = Path(directory) / file['downloaded_path']
        response = requests.get(file_url)

        with open(file_path, 'wb') as f:
            f.write(response.content)

    filename = f'{path}.html'
    filepath = Path(directory) / filename

    with open(filepath, 'w') as f:
        f.write(handled_page_text)
    return str(filepath)
