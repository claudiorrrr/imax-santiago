import logging
import sys
from datetime import datetime
import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cinemark_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def scrape_cinemark_imax():
    logging.info("Starting scraper for Cinemark...")
    movies_data = {
        "last_updated": datetime.now().isoformat(),
        "movies": []
    }

    driver = None
    try:
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Remove headless mode for debugging
        # options.add_argument('--headless')

        # Try to create the driver with specific version and longer page load timeout
        driver = uc.Chrome(
            options=options,
            version_main=132,  # Match your Chrome version
            driver_executable_path=None,  # Let it auto-detect
            browser_executable_path=None,  # Let it auto-detect
            page_load_timeout=30
        )

        wait = WebDriverWait(driver, 30)

        url = "https://www.cinemark.cl/cine?tag=511&cine=cinemark_mallplaza_vespucio"
        logging.info(f"Accessing URL: {url}")

        # Set window size
        driver.set_window_size(1920, 1080)

        # Navigate to the page
        driver.get(url)
        logging.info("Page loaded successfully")

        # Initial wait for page load
        time.sleep(5)

        # Handle cookie modal
        try:
            logging.info("Looking for cookie modal...")
            cookie_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-automation='Btn_acepto_cookies']"))
            )
            logging.info("Cookie button found, clicking...")
            cookie_btn.click()
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Cookie modal handling failed: {str(e)}")

        # Handle theater modal
        try:
            logging.info("Looking for theater modal...")
            theater_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.change-theatre-button button.next"))
            )
            logging.info("Theater button found, clicking...")
            theater_btn.click()
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Theater modal handling failed: {str(e)}")

        # Try to find movies
        try:
            logging.info("Looking for movies container...")
            movies_container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.movies-container"))
            )

            movies = movies_container.find_elements(By.CSS_SELECTOR, "div.movie-item")
            logging.info(f"Found {len(movies)} movies")

            for movie in movies:
                try:
                    imax_tags = movie.find_elements(By.CSS_SELECTOR, "div.movie-version span.tag-IMAX")
                    if imax_tags:
                        title = movie.find_element(By.CSS_SELECTOR, "h3.movie-title").text
                        logging.info(f"Found IMAX movie: {title}")

                        showtimes = []
                        showtime_elements = movie.find_elements(By.CSS_SELECTOR, "a.showtime")
                        for time_elem in showtime_elements:
                            time_text = time_elem.text.strip()
                            time_url = time_elem.get_attribute("href")
                            if time_text:
                                showtimes.append({
                                    "time": time_text,
                                    "url": time_url
                                })

                        if showtimes:
                            movies_data["movies"].append({
                                "title": title,
                                "showtimes": showtimes
                            })

                except Exception as e:
                    logging.error(f"Error processing movie: {str(e)}")
                    continue

        except Exception as e:
            logging.error(f"Error finding movies: {str(e)}")
            # Save page source for debugging
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logging.info("Saved page source to page_source.html")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("Browser closed")
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")

    # Save results
    try:
        with open('cinemark_movies.json', 'w', encoding='utf-8') as f:
            json.dump(movies_data, f, ensure_ascii=False, indent=2)
        logging.info("Successfully saved cinemark_movies.json")
    except Exception as e:
        logging.error(f"Error saving JSON file: {str(e)}")

    return movies_data

if __name__ == "__main__":
    result = scrape_cinemark_imax()
    print("\nScraped Movies:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
