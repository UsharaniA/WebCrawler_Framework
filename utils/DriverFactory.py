import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver
from datetime import datetime
import random
import undetected_chromedriver as uc

# Patch the __del__ method to suppress WinError 6 during garbage collection
uc.Chrome.__del__ = lambda self: None

# Global driver variable to be accessed across modules
global_driver: WebDriver = None

class DriverFactory:
    _drivers = {}

    CHROME_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        # Add more if needed
    ]

    @staticmethod
    def _create_directories(*paths):
        for path in paths:
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def get_driver(browser_name="chrome", download_file_path=None) -> WebDriver:
        global global_driver

        if browser_name not in DriverFactory._drivers:
            headless = os.getenv("HEADLESS_DRIVER", "false").lower() == "true"
            chrome_driver_path = os.path.join(
                os.getcwd(),
                os.getenv("DRIVERS_FOLDER_PATH", "drivers")
            )
            # chrome_driver_path = os.getenv("DRIVERS_FOLDER_PATH", "")


            # chrome_options = ChromeOptions()
            chrome_options = uc.ChromeOptions()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--remote-allow-origins=*")
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--lang=en-US")
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.geolocation": 1  # 2 = Block
            })

             # Rotate User-Agent
            user_agent = random.choice(DriverFactory.CHROME_USER_AGENTS)
            chrome_options.add_argument(f"user-agent={user_agent}")

            if headless:
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")

            service = ChromeService(executable_path=chrome_driver_path)
            # driver = webdriver.Chrome(service=service, options=chrome_options)
            driver = uc.Chrome(options=chrome_options, headless=False)
            # Grant geolocation permission for Waze
            driver.execute_cdp_cmd("Browser.grantPermissions", {
                "origin": "https://www.waze.com",
                "permissions": ["geolocation"]
            })

            # Spoof geolocation to New York City, USA
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "accuracy": 100
            })

            DriverFactory._drivers[browser_name] = driver
            global_driver = driver  # Set the global driver

        return DriverFactory._drivers[browser_name]

    @staticmethod
    def get_driver_instance() -> WebDriver:
        global global_driver
        return global_driver

    @staticmethod
    def close_all_drivers():
        global global_driver
        for key, driver in DriverFactory._drivers.items():
            try:
                driver.quit()
            except Exception as e:
                print(f"Error closing driver {key}: {e}")
        DriverFactory._drivers.clear()
        global_driver = None

    @staticmethod
    def quit_driver(driver: WebDriver) -> bool:
        try:
            driver.quit()
            return True
        except Exception as e:
            print(f"Error quitting driver: {e}")
            return False

    @staticmethod
    def get_screenshot(driver: WebDriver = None) -> str:
        driver = driver or DriverFactory.get_driver_instance()
        if driver is None:
            raise Exception("No active driver found.")

        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        DriverFactory._create_directories(screenshots_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")

        driver.save_screenshot(screenshot_path)
        return screenshot_path
