import os
import logging
from urllib.parse import urlparse, urljoin
from carwlerpkg.crawl import fetch_html, setup_logger, save_html_to_file, extract_links

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = setup_logger()
crawlednun = 0

def crawl(url, uncrawled_list, external_list, root_dir="."):
    """
    Crawls the given URL, saves HTML content, and processes links.

    Args:
    - url (str): The URL to crawl.
    - uncrawled_list (list): List to store uncrawled internal links.
    - external_list (list): List to store external links.
    - root_dir (str): Root directory to save HTML content.
    """
    # Fetch HTML content of the given URL
    html_content = fetch_html(url)
    if html_content:
        logger.info(f"Successfully fetched HTML from {url}")
        # Save HTML content to a file
        save_html_to_file(html_content, url, root_dir=root_dir)

        # Extract links from the HTML content
        links = extract_links(html_content, url)
        for link, is_internal in links:
            if is_internal:
                uncrawled_list.add(link)
            else:
                external_list.add(link)


# Initialize lists to store uncrawled internal links and external links
uncrawled_internal_links = set()
external_links = set()

# Set the initial URL to crawl
initial_url = "https://universe.leagueoflegends.com/en_US/"

# Perform initial crawl
crawl(initial_url, uncrawled_internal_links, external_links)
crawlednun += 1
logger.info(f"Initial crawl OK: {crawlednun}. Uncrawled links: {len(uncrawled_internal_links)}")

# Iterate over uncrawled internal links until the list is empty
while uncrawled_internal_links:
    # Get the next URL from the uncrawled list
    next_url = uncrawled_internal_links.pop()

    # Check if the URL has already been crawled
    if next_url in external_links:
        continue

    # Perform crawl for the next URL
    crawl(next_url, uncrawled_internal_links, external_links)
    crawlednun += 1
    logger.info(f"Linkks crawled: {crawlednun}. Uncrawled links: {len(uncrawled_internal_links)}")

