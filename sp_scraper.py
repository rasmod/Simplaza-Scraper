import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor
from tqdm import asyncio as tqdm_asyncio
import aiohttp
import aiofiles
import ctypes
import asyncio

# Function to download a file from a given link
async def download_file(session, download_link, download_directory):
    try:
        # Extract filename from the URL
        file_name = unquote(download_link.split('&file=')[1].split('&hash=')[0])

        # Download the file
        download_path = os.path.join(download_directory, file_name)
        async with session.get(download_link) as response:
            response.raise_for_status()  # Raise HTTPError for bad responses

            # Use tqdm to display a progress bar
            total_size = int(response.headers.get('content-length', 0))
            with tqdm_asyncio.tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                async with aiofiles.open(download_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        bar.update(len(chunk))
                        await file.write(chunk)

        print(f"Downloaded: {file_name}")

    except Exception as e:
        print(f"Error downloading {download_link}: {e}")

# Function to collect all download links from the website
def collect_download_links(website_url):
    response = requests.get(website_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract download links from anchor tags
    download_links = [link['href'] for link in soup.find_all('a', href=True) if '&file=' in link['href']]

    return download_links

# Function to display a Windows notification
def show_notification(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 1)

async def main():
    # Specify the website URL
    website_url = "https://simplaza.org/torrent-master-list/"

    # Specify the directory to save the downloaded files
    download_directory = os.path.join(os.path.expanduser("~"), "Downloads", "Simplaza_torrents")

    # Create the download directory if it doesn't exist
    os.makedirs(download_directory, exist_ok=True)

    # Collect all download links from the website
    all_download_links = collect_download_links(website_url)

    # Download each file from the collected links using asyncio
    async with aiohttp.ClientSession() as session:
        tasks = [download_file(session, link, download_directory) for link in all_download_links]
        await asyncio.gather(*tasks)

    print("Script execution completed.")

    # Windows notification
    show_notification("Torrent Download", "Downloads completed!")

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
