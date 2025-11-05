import logging

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from lxml import html as lxml_html
import os
import time

from config import config

from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
)


def download_dynamic_html_firefox(url, max_retries=3):
    firefox_driver = None

    for attempt in range(max_retries):
        try:
            options = Options()
            options.page_load_strategy = 'eager'
            options.add_argument('--headless')

            service = Service(
                executable_path=config.GECKODRIVER_PATH
            )

            firefox_driver = webdriver.Firefox(service=service, options=options)

            firefox_driver.set_page_load_timeout(30)
            firefox_driver.implicitly_wait(10)

            firefox_driver.get(url)
            time.sleep(config.SLEEP_INTERVAL)

            source_html_content = firefox_driver.page_source

            if source_html_content and len(source_html_content) > 0:
                return source_html_content
            else:
                raise WebDriverException("Received empty html")

        except TimeoutException as e:
            logging.error(f"Timeout on loading {url} (attempt{attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logging.error(f"Did not succeed for {url}")
                return None
            time.sleep(2)

        finally:
            if firefox_driver:
                try:
                    firefox_driver.quit()
                except Exception as e:
                    logging.warning(f"Error at browser quit: {e}")
                firefox_driver = None

    return None

for page_num in range(1, config.MAX_PAGES):

    url = config.CATALOG_PL_URL.format(page_num)
    html_content = download_dynamic_html_firefox(url)

    tree = lxml_html.fromstring(html_content)
    links = tree.xpath("//a[contains(@class, 'model-short-title')]/@href")
    full_links = [config.BASE_URL + link if link.startswith('/') else link for link in links]
    idx = 1
    for product_url in full_links:
        try:
            product_html = download_dynamic_html_firefox(product_url)
            output_dir = config.OUTPUT_DIR
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, f"page{page_num}_product{idx}.html")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(product_html)
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Error downloading {product_url}: {e}")
        idx += 1

    print(f"Processed page {page_num}, products: {len(full_links)}")
