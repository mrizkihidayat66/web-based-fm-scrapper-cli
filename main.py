import os
import subprocess
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def download_file(file_url, destination_folder):
    """
    Downloads a file from the given URL and saves it to the specified folder.

    Args:
        file_url (str): The URL of the file to be downloaded.
        destination_folder (str): The folder where the file will be saved.
    """
    try:
        file_name = os.path.basename(urlparse(file_url).path)
        file_path = os.path.join(destination_folder, file_name)
        print(f'Downloading: {destination_folder}/{file_name} ...')
        subprocess.run(['wget', '-O', file_path, file_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
    except Exception as e:
        print(f'Error: {str(e)}')

def create_directory_structure(input_url, base_folder, file_url):
    """
    Creates the directory structure for the given file URL inside the base folder.

    Args:
        input_url (str): The base URL where the file manager is located.
        base_folder (str): The base folder where the files will be saved.
        file_url (str): The URL of the file for which directory structure needs to be created.

    Returns:
        str: The path of the directory where the file will be saved.
    """
    parsed_input_url = urlparse(input_url)
    parsed_file_url = urlparse(file_url)

    input_path = parsed_input_url.path
    file_path = parsed_file_url.path

    remaining_path = file_path[len(input_path):].lstrip('/')

    folders = remaining_path.split('/')

    current_path = base_folder
    last_index = len(folders) - 1
    for index, folder in enumerate(folders):
        if index < last_index and not file_url.endswith('/'):
            current_path = os.path.join(current_path, folder)
            os.makedirs(current_path, exist_ok=True)

    return current_path

def scrape_links(url, output_folder):
    """
    Scrapes links from the given URL and downloads files to the specified folder.

    Args:
        url (str): The URL to scrape links from.
        output_folder (str): The folder where the downloaded files will be saved.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            link_elements = soup.find_all('td', class_='link')

            for index, td in enumerate(link_elements):
                link_url = urljoin(url, td.a['href'])

                if index > 0: # skip ../ from eg: ['../', 'dir1', 'file1', ...] url lists
                    created_path = create_directory_structure(input_url, output_folder, link_url)
                    if link_url.endswith('/'):
                        scrape_links(link_url, created_path)
                    else:
                        download_file(link_url, created_path)

    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == '__main__':
    input_url = input("File Manager URL\t: ")
    output_folder = input("Output Path\t\t: ")
    print()

    if not input_url.endswith('/'):
        input_url += '/'

    os.makedirs(output_folder, exist_ok=True)
    scrape_links(input_url, output_folder)
