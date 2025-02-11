import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def list_cinepolis_imax_movies():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')

    print("Checking Cinépolis Plaza Egaña IMAX movies...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(10)

    # Initialize the JSON structure
    movies_data = {
        "last_updated": datetime.now().isoformat(),
        "movies": []
    }

    try:
        url = "https://cinepolischile.cl/cartelera/santiago-oriente/cinepolis-mallplaza-egana"
        driver.get(url)

        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.row.tituloPelicula")))

        movie_articles = driver.find_elements(By.CSS_SELECTOR, "article.row.tituloPelicula")

        print("\nIMAX Movies:")
        print("-" * 40)

        imax_count = 0
        for article in movie_articles:
            try:
                imax_img = article.find_elements(By.CSS_SELECTOR, "img[src*='icon-imax']")
                if imax_img:
                    title = article.find_element(By.CSS_SELECTOR, "a.datalayer-movie.ng-binding")
                    showtime_elements = article.find_elements(By.CSS_SELECTOR, "time.btn.btnhorario a")

                    # Print the original format
                    print(f"- {title.text}")

                    # Create movie entry for JSON
                    movie_entry = {
                        "title": title.text,
                        "showtimes": []
                    }

                    if showtime_elements:
                        print("  Showtimes:")
                        for time_element in showtime_elements:
                            time = time_element.text
                            buy_url = time_element.get_attribute('href')
                            print(f"    {time} - Buy tickets: {buy_url}")

                            # Add showtime to JSON structure
                            movie_entry["showtimes"].append({
                                "time": time,
                                "url": buy_url
                            })
                    else:
                        print("  No showtimes available")
                    print()  # Add blank line between movies

                    # Add movie to JSON data
                    movies_data["movies"].append(movie_entry)
                    imax_count += 1
            except Exception as e:
                continue

        if imax_count == 0:
            print("No IMAX movies found")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    # Save JSON to file
    with open('movies.json', 'w', encoding='utf-8') as f:
        json.dump(movies_data, f, ensure_ascii=False, indent=2)

    # Print JSON output
    print("\nJSON Output:")
    print(json.dumps(movies_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    list_cinepolis_imax_movies()

