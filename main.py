import os
from dotenv import load_dotenv
from utils.selenium_client import *
from utils.parser import *
from selenium.webdriver.common.by import By


# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

def main():
    if not se_open_browser("Chrome", BASE_URL):
        print("Failed to open browser.")
        return
    try:
         navigatetomap()
    finally:
        close_driver()

if __name__ == "__main__":
    main()

