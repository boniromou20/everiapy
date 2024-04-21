import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def download_image(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded {url} to {filename}")

def get_image_urls_and_alts(album_urls):
    all_image_data = []
    for album_url in album_urls:
        response = requests.get(album_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        album_name = soup.find('h1').text
        urls_and_alts = [(img['src'], img.get('alt', ''), album_name) for img in img_tags]
        all_image_data.extend(urls_and_alts)
    return all_image_data

def get_page_urls(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    page_tags = soup.find_all('a', class_='page-numbers')
    urls = [page['href'] for page in page_tags]
    return urls

def get_album_urls(page_urls):
    album_urls = []
    for page_url in page_urls:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        album_tags = soup.find_all('a', class_='thumbnail-link')
        album_urls.extend([album['href'] for album in album_tags])
    return album_urls


def main(url, download_path):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    page_urls = get_page_urls(url)
    album_urls = get_album_urls(page_urls)
    image_data = get_image_urls_and_alts(album_urls)

    with ThreadPoolExecutor(max_workers=8) as executor:
        current_album = None
        counter = 1
        for image_url, alt, album_name in tqdm(image_data, desc="Downloading images"):
            if album_name != current_album:
                current_album = album_name
                counter = 1
            album_path = os.path.join(download_path, album_name)
            if not os.path.exists(album_path):
                os.makedirs(album_path)
            filename = os.path.join(album_path, f"{counter}.jpg")
            if not os.path.exists(filename):
                executor.submit(download_image, image_url, filename)
            counter += 1

if __name__ == "__main__":
    main("https://everia.club/tag/moe-iori-伊織もえ/", "./images/moe-iori-伊織もえ")


