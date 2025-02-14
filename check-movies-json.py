import logging
import sys
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def wait_for_angular(driver):
    script = """
    var callback = arguments[arguments.length - 1];
    if (window.angular) {
        var el = document.querySelector('body');
        var injector = window.angular.element(el).injector();
        var $http = injector.get('$http');
        var $rootScope = injector.get('$rootScope');
        var $timeout = injector.get('$timeout');

        var fn = function() {
            if (!$http.pendingRequests.length) {
                callback(true);
            } else {
                $timeout(fn, 100);
            }
        };
        $timeout(fn, 0);
    } else {
        callback(false);
    }
    """
    try:
        driver.execute_async_script(script)
    except:
        pass
    time.sleep(5)  # Fallback wait

def list_cinepolis_imax_movies():
    logging.info("Starting Chrome WebDriver...")
    movies_data = {
        "last_updated": datetime.now().isoformat(),
        "movies": []
    }

    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        url = "https://cinepolischile.cl/cartelera/santiago-oriente/cinepolis-mallplaza-egana"
        logging.info(f"Accessing URL: {url}")

        driver.get(url)

        # Wait for Angular to load and process data
        wait_for_angular(driver)

        # Wait specifically for IMAX content
        wait = WebDriverWait(driver, 20)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='horarioExp'][class*='IMAX']")))
        except:
            logging.info("Waiting longer for IMAX content...")
            time.sleep(10)  # Additional wait if needed

        movie_articles = driver.find_elements(By.CSS_SELECTOR, "article.row.tituloPelicula")
        logging.info(f"Found {len(movie_articles)} movie articles")

        print("\nIMAX Movies:")
        print("-" * 40)
        imax_count = 0

        for article in movie_articles:
            try:
                # Look for IMAX format div instead of just the image
                imax_format = article.find_elements(By.CSS_SELECTOR, "div[class*='horarioExp'][class*='IMAX']")
                if imax_format:
                    title = article.find_element(By.CSS_SELECTOR, "a.datalayer-movie.ng-binding")
                    logging.info(f"Processing IMAX movie: {title.text}")

                    print(f"- {title.text}")

                    movie_entry = {
                        "title": title.text,
                        "showtimes": []
                    }

                    for format_div in imax_format:
                        print(" IMAX Showtimes:")
                        showtime_elements = format_div.find_elements(By.CSS_SELECTOR, "time.btn.btnhorario a")
                        logging.info(f"Found {len(showtime_elements)} showtimes for {title.text}")

                        for time_element in showtime_elements:
                            showtime = time_element.text
                            buy_url = time_element.get_attribute('href')
                            print(f" {showtime} - Buy tickets: {buy_url}")

                            movie_entry["showtimes"].append({
                                "time": showtime,
                                "url": buy_url
                            })

                    print()

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
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        print(f"An error occurred: {e}")
    finally:
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
