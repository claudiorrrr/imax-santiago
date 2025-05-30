import logging
import sys
import time
import json
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException
import os
import shutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def clear_chrome_cache():
    cache_path = os.path.expanduser('~/.local/share/undetected_chromedriver')
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)

def create_driver(max_retries=3, retry_delay=1):
    options = uc.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    for attempt in range(max_retries):
        try:
            clear_chrome_cache()  # Clear cache before each attempt
            driver = uc.Chrome(
                options=options,
                version_main=132  # Your current Chrome version
            )
            driver.set_page_load_timeout(30)
            return driver
        except SessionNotCreatedException as e:
            logging.warning(f"Driver creation attempt {attempt + 1} failed. Retrying...")
            if attempt == max_retries - 1:
                raise e
            time.sleep(retry_delay)

def list_cinepolis_imax_movies():
    logging.info("Starting Chrome WebDriver...")
    movies_data = {
        "last_updated": datetime.now().isoformat(),
        "movies": []
    }
    driver = None

    try:
        driver = create_driver()
        url = "https://cinepolischile.cl/cartelera/santiago-oriente/cinepolis-mallplaza-egana"
        logging.info(f"Accessing URL: {url}")

        try:
            driver.get(url)
            # Increased initial wait time
            time.sleep(15)

            # Wait for specific element with increased timeout
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.row.tituloPelicula")))

            # Execute JavaScript to scroll down the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            movie_articles = driver.find_elements(By.CSS_SELECTOR, "article.row.tituloPelicula")
            logging.info(f"Found {len(movie_articles)} movie articles")

            print("\nIMAX Movies:")
            print("-" * 40)
            imax_count = 0

            for article in movie_articles:
                try:
                    # Look for IMAX format div
                    imax_format = article.find_elements(By.CSS_SELECTOR, "div[class*='horarioExp'][class*='IMAX']")
                    if imax_format:
                        title_element = article.find_element(By.CSS_SELECTOR, "a.datalayer-movie.ng-binding")
                        title = title_element.get_attribute('text') or title_element.text
                        logging.info(f"Processing IMAX movie: {title}")

                        print(f"- {title}")

                        movie_entry = {
                            "title": title,
                            "showtimes": []
                        }

                        for format_div in imax_format:
                            print(" IMAX Showtimes:")
                            showtime_elements = format_div.find_elements(By.CSS_SELECTOR, "time.btn.btnhorario a")
                            logging.info(f"Found {len(showtime_elements)} showtimes for {title}")

                            for time_element in showtime_elements:
                                showtime = time_element.get_attribute('text') or time_element.text
                                buy_url = time_element.get_attribute('href')
                                if showtime and buy_url:
                                    print(f" {showtime} - Buy tickets: {buy_url}")
                                    movie_entry["showtimes"].append({
                                        "time": showtime,
                                        "url": buy_url
                                    })

                        if movie_entry["showtimes"]:
                            movies_data["movies"].append(movie_entry)
                            imax_count += 1

                except Exception as e:
                    logging.error(f"Error processing movie article: {str(e)}", exc_info=True)
                    continue

            if imax_count == 0:
                logging.warning("No IMAX movies found")
                print("No IMAX movies found")

        except Exception as e:
            logging.error(f"Error accessing URL: {str(e)}", exc_info=True)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        print(f"An error occurred: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("WebDriver closed successfully")
            except Exception as e:
                logging.error("Error closing WebDriver", exc_info=True)

    try:
        with open('movies.json', 'w', encoding='utf-8') as f:
            json.dump(movies_data, f, ensure_ascii=False, indent=2)
        logging.info("Successfully saved movies.json")
    except Exception as e:
        logging.error(f"Error saving JSON file: {str(e)}", exc_info=True)

    print("\nJSON Output:")
    print(json.dumps(movies_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    list_cinepolis_imax_movies()
