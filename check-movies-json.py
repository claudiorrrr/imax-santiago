import logging
import sys
import time
import json
from datetime import datetime
from seleniumbase import Driver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def list_cinepolis_imax_movies():
    logging.info("Starting Chrome WebDriver...")
    movies_data = {
        "last_updated": datetime.now().isoformat(),
        "movies": []
    }

    try:
        driver = Driver(uc=True, headless=True)  # Use SeleniumBase's UC Mode
        url = "https://cinepolischile.cl/cartelera/santiago-oriente/cinepolis-mallplaza-egana"
        logging.info(f"Accessing URL: {url}")

        driver.get(url)
        driver.sleep(5)  # Built-in sleep method

        movie_articles = driver.find_elements("css selector", "article.row.tituloPelicula")
        logging.info(f"Found {len(movie_articles)} movie articles")

        print("\nIMAX Movies:")
        print("-" * 40)
        imax_count = 0

        for article in movie_articles:
            try:
                imax_img = article.find_elements("css selector", "img[src*='icon-imax']")
                if imax_img:
                    title = article.find_element("css selector", "a.datalayer-movie.ng-binding")
                    logging.info(f"Processing IMAX movie: {title.text}")

                    imax_showtime_container = article.find_elements("css selector", "div[class*='horarioExp'][class*='IMAX']")

                    print(f"- {title.text}")

                    movie_entry = {
                        "title": title.text,
                        "showtimes": []
                    }

                    if imax_showtime_container:
                        print(" IMAX Showtimes:")
                        for container in imax_showtime_container:
                            showtime_elements = container.find_elements("css selector", "time.btn.btnhorario a")
                            logging.info(f"Found {len(showtime_elements)} showtimes for {title.text}")

                            for time_element in showtime_elements:
                                showtime = time_element.text
                                buy_url = time_element.get_attribute('href')
                                print(f" {showtime} - Buy tickets: {buy_url}")

                                movie_entry["showtimes"].append({
                                    "time": showtime,
                                    "url": buy_url
                                })
                    else:
                        logging.info(f"No IMAX showtimes available for {title.text}")
                        print(" No IMAX showtimes available")

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
