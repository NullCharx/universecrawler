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
    Fetches the HTML content of a webpage.

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
    links = []
    soup = BeautifulSoup(html_content, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('#'):
            continue
        absolute_url = urljoin(base_url, href)
        parsed_url = urlparse(absolute_url)
        is_internal = parsed_url.netloc == urlparse(base_url).netloc
        links.append((absolute_url, is_internal))
    return links



def fetch_html_with_selenium(url):
    # Initialize a Selenium WebDriver (make sure to provide the path to the WebDriver executable)
    driver = webdriver.Chrome()  # Example for Chrome, you can use other browsers as well

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for dynamic content to load (replace this with appropriate wait conditions)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.dynamic-content")))

        # Get the HTML content
        html_content = driver.page_source
    finally:
        # Make sure to close the browser window
        driver.quit()

    return html_content