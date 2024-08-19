import os
import requests_mock
from heclet_code.page_loader import download


def test_download(tmpdir):
    url = "https://ru.hexlet.io/courses"
    expected_filename = "ru-hexlet-io-courses.html"
    expected_file_path = os.path.join(tmpdir, expected_filename)

    with requests_mock.Mocker() as mock:
        mock.get(url, text="<html></html>")
        file_path = download(url, tmpdir)

    assert file_path == expected_file_path
    assert os.path.exists(file_path)
