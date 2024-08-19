import os
import requests


def download(url, output_dir=os.getcwd()):
    response = requests.get(url)
    response.raise_for_status()

    parsed_url = url.replace('https://', '').replace('http://', '')
    filename = parsed_url.replace('/', '-').replace('.', '-') + '.html'
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as file:
        file.write(response.text)

    return filepath
