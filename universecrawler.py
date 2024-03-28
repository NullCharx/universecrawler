import os
import logging
import traceback
import atexit
from urllib.parse import urlparse, urljoin
from carwlerpkg.crawl import fetch_html, setup_logger, save_html_to_file, extract_links, fetch_html_with_selenium, mark_url_as_crawled, is_url_crawled

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
    try:
        # Fetch HTML content of the given URL
        html_content = fetch_html_with_selenium(url)
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
    except Exception as e:
        logger.error(f"Failed to crawl URL: {url}")
        logger.error(traceback.format_exc())

def save_uncrawled_urls(uncrawled_internal_links, uncrawled_pages_file):
    with open(uncrawled_pages_file, 'w') as f:
        for url in uncrawled_internal_links:
            f.write(url + '\n')

def cleanup(uncrawled_internal_links, uncrawled_pages_file):
    # Save uncrawled URLs to a file
    save_uncrawled_urls(uncrawled_internal_links, uncrawled_pages_file)

# Initialize lists to store uncrawled internal links and external links
uncrawled_internal_links = set()
external_links = set()
crawled_urls_file = "crawled_urls.txt"
uncrawled_pages_file = "uncrawled_pages.txt"

# Check if the file containing uncrawled URLs is empty
if os.path.getsize(uncrawled_pages_file) > 0:
    # If the file is not empty, read the first URL from the file
    with open(uncrawled_pages_file, 'r') as f:
        initial_url = f.readline().strip()
    # Remove the first URL from the file
    with open(uncrawled_pages_file, 'r') as f:
        lines = f.readlines()
    with open(uncrawled_pages_file, 'w') as f:
        f.writelines(lines[1:])
    uncrawled_internal_links.update([url.strip() for url in lines[1:]])

else:
    # If the file is empty, set the initial URL to crawl
    initial_url = "https://universe.leagueoflegends.com/en_US/"

# Register cleanup function to be called on exit
atexit.register(cleanup, uncrawled_internal_links, uncrawled_pages_file)

# Perform initial crawl
for url in list(uncrawled_internal_links):
    crawl(url, uncrawled_internal_links, external_links)
    mark_url_as_crawled(url, crawled_urls_file)
    uncrawled_internal_links.remove(url)
    crawlednun += 1
    logger.info(f"Initial crawl OK: {crawlednun}. Uncrawled links: {len(uncrawled_internal_links)}")

# Iterate over uncrawled internal links until the list is empty
while uncrawled_internal_links:
    # Get the next URL from the uncrawled list
    next_url = uncrawled_internal_links.pop()

    # Perform crawl for the next URL
    crawl(next_url, uncrawled_internal_links, external_links)
    mark_url_as_crawled(next_url, crawled_urls_file)
    crawlednun += 1
    logger.info(f"Linkks crawled: {crawlednun}. Uncrawled links: {len(uncrawled_internal_links)}")
