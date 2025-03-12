def find_flight_price(flight_origin, flight_destination, departure_date, return_date=None):
    """
    This function finds the "Best" price in Kayak given an origin, destination, departure date, and optional return_date.
        - flight_origin: 3-letter code of the airport/area. Use find_kayak_airport function to find it.
        - flight_destination: 3-letter code of the airport/area. Use find_kayak_airport function to find it.
        - departure_date: Date in YYYY-MM-DD format.
        - return_date: Date in YYYY-MM-DD format. Optional value. If not used, will find one-way flights.
    """
    import time
    import re
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager

    # Set up Chrome options for headless mode
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    # Use ChromeDriverManager to automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Create a new instance of Chrome in headless mode
    browser = webdriver.Chrome(service=service, options=options)

    try:
        # Determine if the trip is one-way or round trip, and use the proper URL
        if return_date is None:
            kayak_url = f"https://www.kayak.es/flights/{flight_origin}-{flight_destination}/{departure_date}?ucs=1993xcp"
        else:
            kayak_url = f"https://www.kayak.es/flights/{flight_origin}-{flight_destination}/{departure_date}/{return_date}?ucs=1993xcp"

        # Open the Kayak URL
        browser.get(kayak_url)

        # Wait for the page to load (adjust timing as needed)
        time.sleep(20)

        # Find all elements with the class name 'Hv20-value'
        all_prices = browser.find_elements(By.CLASS_NAME, 'Hv20-value')

        # Check if there are at least two elements
        if len(all_prices) >= 2:
            # Get the second element
            second_price = all_prices[1].text  # Access the second element (index 1)

            # Clean the text to extract the numeric part
            price_number = re.search(r'\d+', second_price)
            if price_number:
                price_number = price_number.group()  # Extract the matched number
                price_number = int(price_number)
            else:
                print('Number not found in "El Mejor".')
                price_number = None
        else:
            print('There is no element "El mas barato" or "El Mejor".')
            price_number = None

    except Exception as e:
        print(f"An error occurred: {e}")
        price_number = None
    finally:
        # Close the browser
        browser.quit()

    return price_number
