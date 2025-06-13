from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from .excel_writer import write_to_excel
import os
import requests
import time
# from .DriverFactory  import global_driver
from .sleep_utils import random_sleep
from .DriverFactory import DriverFactory

# Externalized selectors and field keys
EXCEL_FILE = os.getenv("EXCEL_FILE", "scraped_data.xlsx")

SELECTORS = {
    # Each listing block is a div with this specific class
    "listing_block": ("div", "StyledPropertyCardDataWrapper-c11n-8-109-3__sc-hfbvv9-0"),
    
    # Title seems to be the <a> tag with this class (property link)
    "title": ("a", "StyledPropertyCardDataArea-c11n-8-109-3__sc-10i1r6-0"),
    
    # Location is inside <address> tag within the <a> (no specific class shown in snippet)
    "location": ("address", ""),
    
    # Price is a <span> with class "PropertyCardWrapper__StyledPriceLine-srp-8-109-3__sc-16e8gqd-1"
    "price": ("span", "PropertyCardWrapper__StyledPriceLine-srp-8-109-3__sc-16e8gqd-1")
}

FIELD_KEYS = {
    "title": "title",
    "location": "location",
    "price": "price",
    "url": "url"
}

def parse_Data_listings(html, base_url):
    all_listings = []
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    # Find all listing blocks
    listing_blocks = soup.find_all(*SELECTORS["listing_block"])

    for block in listing_blocks:
        # Extract title and URL
        title_tag = block.select_one(SELECTORS["title"][0])
        title = title_tag.text.strip() if title_tag else "N/A"
        url = urljoin(base_url, title_tag.get('href')) if title_tag else "N/A"

        # Extract location
        location_tag = block.select_one(SELECTORS["location"][0])
        location = location_tag.text.strip().replace("Land in", "").strip() if location_tag else "N/A"

        # Extract price
        price_tag = block.select_one(SELECTORS["price"][0])
        price = price_tag.text.strip() if price_tag else "N/A"

        listings.append({
            FIELD_KEYS["title"]: title,
            FIELD_KEYS["location"]: location,
            FIELD_KEYS["price"]: price,
            FIELD_KEYS["url"]: url
        })

    for listing in listings:
        title = listing.get("title", "")
        url = listing.get("url", "")
        price = parse_price(listing.get("price", "0"))
        beds = int(listing.get("beds", 0))
        listing_id = f"{title}-{url}"

        all_listings.append([title, url,price])

    if all_listings:
        print(f"Writing to Excel")
        write_to_excel(EXCEL_FILE, "House Listings", ["Title", "URL","Price"], all_listings)

    return listings


def parse_price(price_str):
    """
    Parses Indian real estate price strings like '₹96.7 L - 1.25 Cr' and returns the lower bound as an integer (in rupees).
    """
    if not price_str:
        return 0

    price_str = price_str.replace('₹', '').replace(',', '').strip().upper()

    # Handle price range like '96.7 L - 1.25 Cr'
    if '-' in price_str:
        price_str = price_str.split('-')[0].strip()

    try:
        if 'CR' in price_str:
            return int(float(price_str.replace('CR', '').strip()) * 1e7)
        elif 'L' in price_str:
            return int(float(price_str.replace('L', '').strip()) * 1e5)
        else:
            return int(float(price_str))  # fallback
    except ValueError:
        return 0  # If format is invalid


def se_click_using_javascript(driver: WebDriver, test_object: WebElement) -> bool:
    object_found = False
    try:
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", test_object)
        # Click using JavaScript
        driver.execute_script("arguments[0].click();", test_object)
        object_found = True
    except NoSuchElementException as nse:
        print(f"NoSuchElementException: {nse}")
        object_found = False
    except Exception as e:
        print(f"Exception: {e}")
        object_found = False

    return object_found

def parse_Data_listingsagent(html, base_url):
      

        all_listings = []
        driver = DriverFactory.get_driver_instance()
        soup = BeautifulSoup(html, "html.parser")
        # repo = PageObjectsRepository(global_driver)
        main_window = driver.current_window_handle

        placard_links = soup.find_all("div", class_="agent-placard-link")

        for placard in placard_links:
            block = placard.find("div", class_="details-container")
            if not block:
                continue

            agent_name_tag = block.find("p", class_="agent-name")
            company_tag = block.find("p", class_="company")
            phone_tag = block.find("p", class_="phone")
            total_sales_tag = block.find("p", class_="total-sales")
            deals_area_tag = block.find("p", class_="deals-area")
            price_range_tag = block.find("p", class_="price-range")

            agent_name = agent_name_tag.text.strip() if agent_name_tag else "N/A"
            company = company_tag.text.strip() if company_tag else "N/A"
            phone = phone_tag.text.strip() if phone_tag else "N/A"
            total_sales = total_sales_tag.text.strip() if total_sales_tag else "N/A"
            deals_area = deals_area_tag.text.strip() if deals_area_tag else "N/A"
            price_range = price_range_tag.text.strip() if price_range_tag else "N/A"

            a_tag = placard.find("a", href=True)
            href = a_tag["href"] if a_tag else "N/A"
            full_url = urljoin(base_url, href) if href != "N/A" else "N/A"

            total_value = average_price = profile_price_range = "N/A"

            if full_url != "N/A":
                try:
                    driver.execute_script(f"window.open('{full_url}', '_blank');")
                    # random_sleep(2, 3)

                    new_tab = [h for h in driver.window_handles if h != main_window][-1]
                    driver.switch_to.window(new_tab)

                    # random_sleep(2, 3)    
                    profile_html = driver.page_source

                    profile_stats = scrape_profile_details(profile_html)
                    total_value = profile_stats.get("Total Value", "N/A")
                    profile_price_range = profile_stats.get("Price Range", "N/A")
                    average_price = profile_stats.get("Average Price", "N/A")
                    # Extract additional details
                    home_types = profile_stats.get("Home Types", "N/A")
                    education = profile_stats.get("Education", "N/A")
                    experience = profile_stats.get("Experience", "N/A")
                    websitelink = profile_stats.get("Websitelink", "N/A")

                    driver.close()
                    driver.switch_to.window(main_window)

                except Exception as e:
                    print(f"Error scraping profile for {agent_name}: {str(e)}")
                    driver.switch_to.window(main_window)

            all_listings.append([
                agent_name,
                company,
                phone,
                total_sales,
                deals_area,
                price_range,
                full_url,
                total_value,
                profile_price_range,
                average_price,
                home_types,
                education,
                experience,
                websitelink

            ])

        if all_listings:
            print("Writing to Excel")
            write_to_excel(
                EXCEL_FILE,
                "Agent Listings",
                ["Agent Name", "Company", "Phone", "Total Sales", "Deals Area", "Card Price Range",
                 "Profile URL", "Total Value", "Profile Price Range", "Average Price", "Home Type","Education","Experience", "Websitelink"],
                all_listings
            )

        return all_listings




def scrape_profile_details(html):  

    total_value = extract_stat_value_by_label(html,"Total Value")
    price_range = extract_stat_value_by_label(html,"Price Range")
    average_price = extract_stat_value_by_label(html,"Average Price")
    home_types = extract_quick_info_value_by_label(html, "Home Types")
    experience = extract_quick_info_value_by_label(html, "Years of Experience")
    education = extract_quick_info_value_by_label(html, "Education")
    websitelink=get_agent_website(html)
 
                        

    return {
        "Total Value": total_value,
        "Price Range": price_range,
        "Average Price": average_price,
        "Home Types": home_types,
        "Education": education, 
        "Experience" :experience,
        "Websitelink": websitelink
    }


def extract_stat_value_by_label(html, label_text):
    soup = BeautifulSoup(html, "html.parser")

    stat_items = soup.find_all("span", class_="stat-item")

    for stat in stat_items:
        value_tag = stat.find("span", class_="info-bold larger")
        label_tag = value_tag.find_next_sibling("span") if value_tag else None

        if label_tag and label_text.lower() in label_tag.text.strip().lower():
            return value_tag.text.strip()

    return "N/A"


def get_agent_website(html):
    soup = BeautifulSoup(html, "html.parser")
    website_link_tag = soup.find("a", class_="website-link")
    return website_link_tag['href'] if website_link_tag else "N/A"



def extract_quick_info_value_by_label(html, label_text):
    soup = BeautifulSoup(html, "html.parser")
    info_blocks = soup.select("div.quick-info-container div.info-bold")

    for block in info_blocks:
        label = block.get_text(separator=" ", strip=True).split(":")[0].strip()
        if label_text.lower() in label.lower():
            span = block.find("span", class_="info-light")
            return span.text.strip() if span else "N/A"

    return "N/A"