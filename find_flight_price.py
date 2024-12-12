def find_flight_price(flight_origin, flight_destination, departure_date, return_date=None):
    """
    This function finds the "Best" price in Kayak given an origin, destination, departure date, and optional date_return
        - flight_origin: 3 letter name of the airport/ area. Use find_kayak_airport function to find it
        - flight_destination: 3 letter name of the airport/ area. Use find_kayak_airport function to find it
        - departure_date: Date in YYYY-MM-DD format
        - return_date: Date in YYYY-MM-DD format. Optional value. If not used, will find one-way flights
    
    """
    import time
    import re
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # Paths to use Brave instead of Chrome. This is to avoid unwanted ads
    driver_path = r"C:\Users\xavie\OneDrive\Documentos\Ironhack\Week 9 - Final Project\chromedriver.exe"
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    # Set Chrome options
    options = Options()
    options.binary_location = brave_path

    # Create Service object
    service = Service(driver_path)

    # Create new instance of Chrome
    browser = webdriver.Chrome(service=service, options=options)
    import tkinter as tk

    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    # Resize browser to match screen dimensions
    browser.set_window_size(screen_width, screen_height)

    # Determine if the trip is one-way or round trip, and use the proper URL
    if return_date is None:
        kayak_url = f"https://www.kayak.es/flights/{flight_origin}-{flight_destination}/{departure_date}?ucs=1993xcp"
    else:
        kayak_url = f"https://www.kayak.es/flights/{flight_origin}-{flight_destination}/{departure_date}/{return_date}?ucs=1993xcp"

    # Open a website
    browser.get(kayak_url)

    # Wait for 10 seconds for Kayak to load the lowest price in the "El Mejor" section
    time.sleep(20)

    # Find all elements with the class name
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
    else:
        print('There is no element "El mas barato" or "El Mejor".')

    browser.close()

    return price_number

