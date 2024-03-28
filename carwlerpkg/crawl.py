from urllib.parse import urlparse, urljoin
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logging
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_logger():
    # Create a logger
    logger = logging.getLogger("html_fetch_logger")
    logger.setLevel(logging.INFO)

    # Create a file handler and set its level to ERROR
    file_handler = logging.FileHandler("./log.log")
    file_handler.setLevel(logging.INFO)

    # Create a formatter and set the format for the log messages
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger


def fetch_html(url):
    """
    Fetches the HTML content of a webpage, statically.

    Args:
    - url (str): The URL of the webpage to fetch.

    Returns:
    - str or None: The HTML content of the webpage if successful, None otherwise.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the HTML content of the page
            return response.text
        else:
            # If the request was not successful, return None
            return None
    except requests.exceptions.RequestException as e:
        # If an exception occurs during the request, return None
        return None


def download_resources(html_content, base_url, save_dir):
    """
    Downloads resources (images, scripts, stylesheets, etc.) from the HTML content of a webpage.
    This is made to download all resources that are linked in the HTML content of a webpage.
    If the resource is an external URL, it will be skipped.

    Args:
    - html_content (str): The HTML content of the webpage.
    - base_url (str): The base URL of the webpage.
    - save_dir (str): The directory to save the downloaded resources.

    Returns:
    - list: List of tuples containing (link, is_internal).
    """

    soup = BeautifulSoup(html_content, 'html.parser')

    # Set to store downloaded resource URLs
    downloaded_urls = set()

    # Load previously downloaded URLs from a file, if it exists
    downloaded_urls_file = os.path.join(save_dir, 'downloaded_urls.txt')
    if os.path.exists(downloaded_urls_file):
        with open(downloaded_urls_file, 'r') as f:
            downloaded_urls = set(f.read().splitlines())

    for tag in soup.find_all(['img', 'script', 'link', 'source', 'a']):
        # Get the attribute that contains the resource URL
        if tag.name == 'img':
            resource_url = tag.get('src')
        elif tag.name == 'script':
            resource_url = tag.get('src')
        elif tag.name == 'link':
            resource_url = tag.get('href')
        elif tag.name == 'source':
            resource_url = tag.get('src')
        elif tag.name == 'a':
            resource_url = tag.get('href')
        else:
            continue



        # Construct absolute URL
        absolute_url = urljoin(base_url, resource_url)

        # Parse the URL to extract path
        parsed_url = urlparse(absolute_url)
        if parsed_url.netloc != urlparse(base_url).netloc:
            continue

        # Get the directory path relative to the base URL
        relative_path = os.path.relpath(parsed_url.path, os.path.dirname(urlparse(base_url).path))

        # Construct the local directory where the resource will be saved
        local_dir = os.path.join(save_dir, os.path.dirname(relative_path))
        os.makedirs(local_dir, exist_ok=True)

        # Check if resource has already been downloaded
        if absolute_url not in downloaded_urls:
            try:
                response = requests.get(absolute_url)
                if response.status_code == 200:
                    # Extract the filename from the URL
                    filename = os.path.basename(parsed_url.path)
                    # Save the resource to the specified directory
                    with open(os.path.join(local_dir, filename), 'wb') as f:
                        f.write(response.content)
                    # Add the URL to the downloaded set and update the file
                    downloaded_urls.add(absolute_url)
            except Exception as e:
                print(f"Error downloading resource {absolute_url}: {e}")

    # Update the file with the set of downloaded URLs
    with open(downloaded_urls_file, 'a') as f:
        for url in downloaded_urls:
            f.write(url + '\n')


def is_url_crawled(url, crawled_urls_file):
    # Check if the file exists
    if not os.path.exists(crawled_urls_file):
        return False

    # Check if the URL is in the file
    with open(crawled_urls_file, 'r') as f:
        crawled_urls = f.read().splitlines()

    return url in crawled_urls


def save_html_to_file(html_content, url, root_dir="."):
    """
    Saves HTML content to a file.

    Args:
    - html_content (str): The HTML content to be saved.
    - url (str): The URL of the webpage.
    - root_dir (str): Root directory to save HTML content.
    """
    # Parse the URL
    parsed_url = urlparse(url)

    # Generate file path based on URL structure
    if parsed_url.path.endswith('/'):
        filepath = os.path.join(root_dir, parsed_url.netloc, parsed_url.path.lstrip("/"), "index.html")
    else:
        filepath = os.path.join(root_dir, parsed_url.netloc, parsed_url.path.lstrip("/"))

    # Create directories recursively if they don't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Save HTML content to file with UTF-8 encoding
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)


def extract_links(html_content, base_url):
    """
    Extracts links from HTML content and categorizes them as internal or external.

    Args:
    - html_content (str): The HTML content of the webpage.
    - base_url (str): The base URL of the webpage.

    Returns:
    - list: List of tuples containing (link, is_internal).
    """
    # Parse the HTML content
    links = []
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract links from the HTML content (href attribute of <a> tags) and categorize them as internal or external
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Ignore intra-page section links
        if href.startswith('#'):
            continue
        # Join the URL with the base URL to handle relative links
        absolute_url = urljoin(base_url, href)
        # Check if the link is internal or external
        parsed_url = urlparse(absolute_url)
        is_internal = parsed_url.netloc == urlparse(base_url).netloc
        links.append((absolute_url, is_internal))
    return links

def mark_url_as_crawled(url, crawled_urls_file):
    """
    Marks a URL as crawled by adding it to the list of crawled URLs.

    Args:
    - url (str): The URL to mark as crawled.
    - crawled_urls_file (str): The path to the file storing crawled URLs.
    """
    with open(crawled_urls_file, 'a') as f:
        f.write(url + '\n')

def fetch_html_with_selenium(url):
    """
    Uses Selenium to extract HTML content of a dynamically generated webpage.
    In a dynamic webpage, the content is generated using JavaScript after the initial HTML is loaded, so a static
    crawl will lend an html in which only the script tags and empty divs are present.
    In a dynamic crawl, the browser is automated to load the page and wait for the dynamic content to load.
    Once the content is loaded, the HTML content is extracted.

    Args:
    - url (str): The URL of the webpage.

    """
    driver = webdriver.Chrome()  # Example for Chrome, you can use other browsers as well

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for dynamic content to load: Universe page contents loads in a container divisor with id "App"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "App")))

        # Get the HTML content
        html_content = driver.page_source
    finally:
        # Close the window afterwards
        driver.quit()

    return html_content
