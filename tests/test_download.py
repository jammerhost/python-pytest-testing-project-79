import os.path

import pytest
import requests_mock

from hexlet_code.page_loader import download, make_path_by_url


def get_file_bytes(filename: str) -> bytes:
    with open(filename, 'rb') as f:
        return f.read()


def get_file_text(filename: str) -> str:
    with open(filename, 'r') as f:
        return f.read()


def get_file_fixture_name(filename: str) -> str:
    return f'tests/file_fixtures/{filename}'


def get_file_fixture_text(filename: str) -> str:
    return get_file_text(get_file_fixture_name(filename))


def test_download_simple_success(tmp_path, requests_mock):
    url = 'https://example.com/simple'
    expected_file_name = 'example-com-simple.html'
    expected_text = get_file_fixture_text('simple.html')
    requests_mock.get(url, text=expected_text)

    file_path = download(url, str(tmp_path))

    assert file_path == str(tmp_path / expected_file_name)
    with open(file_path) as f:
        assert f.read() == expected_text


@pytest.mark.parametrize(
    ('url', 'path'),
    (
        ('https://example.com/simple.html', 'example-com-simple-html'),
        ('https://sub-domain.example.com/a_b(1)+23-__--5',
         'sub-domain-example-com-a-b-1--23-----5'),
        ('https://ru.hexlet.io/assets/professions/python',
         'ru-hexlet-io-assets-professions-python'),
    )
)
def test_make_path_by_url(url, path):
    assert make_path_by_url(url) == path


def test_download_html_with_files(tmp_path):
    url = 'https://ru.hexlet.io/courses'

    image_url = 'https://ru.hexlet.io/assets/professions/python.png'
    image_path = str(
        tmp_path / 'ru-hexlet-io-courses_files/ru-hexlet-io-assets-professions-python.png')
    image_content = get_file_bytes(get_file_fixture_name('python.png'))

    css_link_url = 'https://ru.hexlet.io/assets/application.css'
    css_link_path = str(
        tmp_path / 'ru-hexlet-io-courses_files/ru-hexlet-io-assets-application.css')
    css_link_content = get_file_bytes(get_file_fixture_name('application.css'))

    html_link_url = 'https://ru.hexlet.io/courses'
    html_link_path = str(
        tmp_path / 'ru-hexlet-io-courses_files/ru-hexlet-io-courses.html')
    html_link_content = get_file_bytes(
        get_file_fixture_name('html-with-files.html'))

    script_url = 'https://ru.hexlet.io/packs/js/runtime.js'
    script_path = str(
        tmp_path / 'ru-hexlet-io-courses_files/ru-hexlet-io-packs-js-runtime.js')
    script_content = get_file_bytes(get_file_fixture_name('runtime.js'))

    with requests_mock.Mocker() as req_mock:
        req_mock.get(url, text=get_file_fixture_text('html-with-files.html'))
        req_mock.get(image_url, content=image_content)
        req_mock.get(css_link_url, content=css_link_content)
        req_mock.get(html_link_url, content=html_link_content)
        req_mock.get(script_url, content=script_content)

        html_path = download(url, str(tmp_path))

    expected_downloaded_html = get_file_fixture_text(
        'html-with-files-downloaded.html')
    assert get_file_text(html_path) == expected_downloaded_html

    assert os.path.exists(image_path)
    assert get_file_bytes(image_path) == image_content

    assert os.path.exists(css_link_path)
    assert get_file_bytes(css_link_path) == css_link_content

    assert os.path.exists(html_link_path)
    assert get_file_bytes(html_link_path) == html_link_content

    assert os.path.exists(script_path)
    assert get_file_bytes(script_path) == script_content

    assert len(os.listdir(str(tmp_path / 'ru-hexlet-io-courses_files'))) == 4
