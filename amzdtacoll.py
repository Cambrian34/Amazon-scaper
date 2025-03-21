import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup
import csv

# Setup WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (no UI)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL of Amazon category page (change this to your desired category)
amazon_category_url = "https://www.amazon.com/s?i=pets&rh=n%3A2619533011&s=popularity-rank&fs=true&ref=lp_2619533011_sar"

# Open the category page
driver.get(amazon_category_url)
time.sleep(3)  # Allow time for dynamic elements to load

# Scroll down to load more products
for _ in range(3):
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(2)

# Get the page source
page_source = driver.page_source

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Find price elements
price_elements = soup.find_all('div', {'data-cy': 'price-recipe'})

prices = []

for price_element in price_elements:
    main_price_span = price_element.find('span', class_='a-offscreen')
    if main_price_span:
        prices.append(main_price_span.text)

# Print the prices
#for price in prices:
#    print(price)

# Find title elements
title_elements = soup.find_all('h2', class_='a-size-base-plus') #Changed this line!
titles = []

for title_element in title_elements:
    title_span = title_element.find('span')
    if title_span:
        titles.append(title_span.text.strip())

# Print the titles, debugging
#for title in titles:
#    print(title)




# Find product image elements
image_elements = driver.find_elements(By.CSS_SELECTOR, "img.s-image")

# Extract image URLs
image_urls = [img.get_attribute("src") for img in image_elements]

# Save the images to a folder
folder = "amazon_images"
os.makedirs(folder, exist_ok=True)

for url in image_urls:
    filename = os.path.join(folder, os.path.basename(url))
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Downloaded: {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

# Print the URLs of the images for debugging
#for url in image_urls:
#    print(url)

# Ensure prices, titles, and image_urls have the same length
min_length = min(len(prices), len(titles), len(image_urls))
prices = prices[:min_length]
titles = titles[:min_length]
image_urls = image_urls[:min_length]

# Define the CSV file path
csv_file_path = "amazon_products.csv"

# Write to CSV file
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Price", "Image Name"])  # Write the header
    for title, price, image_url in zip(titles, prices, image_urls):
        image_name = os.path.basename(image_url)
        writer.writerow([title, price, image_name])

print(f"Data has been written to {csv_file_path}")


# Close the browser
driver.quit()