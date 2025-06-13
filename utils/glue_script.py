import time
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

from selenium.webdriver.common.action_chains import ActionChains
from utils import driver_context
from utils.PageObjectsRepository import PageObjectsRepository
from .excel_writer import write_to_excel
from .selenium_client import *
import re
import traceback





def handle_got_it_popupwait(driver):
    try:
        # Wait for "Got it" to appear (adjust timeout if needed)
        got_it_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Got it']"))
        )
        # got_it_button.click()
        driver.execute_script("arguments[0].click();", got_it_button)
        # print(f"[INFO] Got it' pop-up closed.")
    except:
        print(f"[INFO] Got it' pop-up not present or already dismissed.")


def handle_got_it_popup(driver):
    try:
        # Try to find the button quickly without long wait
        got_it_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='Got it']")
        if got_it_buttons:
            driver.execute_script("arguments[0].click();", got_it_buttons[0])
            print(f"[INFO] Got it' pop-up closed.")
        else:
            print(f"[INFO] Got it' pop-up not present.")
    except Exception as e:
        print(f"Error handling 'Got it' popup: {e}")

def select_schedule_option(driver, option_text="Arrive at"):
    try:
        # Step 1: Click on "Leave now"
        leave_now_xpath = "//div[@data-hook='SCHEDULE_BUTTON']//div[contains(@class, 'wz-react-dropdown__head')]"
        leave_now_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, leave_now_xpath))
        )

        # Use ActionChains or JS to click
        driver.execute_script("arguments[0].scrollIntoView(true);", leave_now_element)
        driver.execute_script("arguments[0].click();", leave_now_element)

        # Step 2: Wait for dropdown to appear and find the "Arrive at" option
        dropdown_option_xpath = f"//div[contains(@class,'wz-react-dropdown__list-container')]//div[normalize-space()='{option_text}']"
        
        option_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, dropdown_option_xpath))
        )

        # Click the desired option using ActionChains
        ActionChains(driver).move_to_element(option_element).pause(0.2).click().perform()
        print(f"Selected: {option_text}")

    except Exception as e:
        print(f"⚠️ Error selecting schedule option: {e}")



def navigatetomap():
    try:
        driver = driver_context.global_driver
        if driver is None: raise Exception("WebDriver not initialized. Call se_open_browser() first.")

        repo = PageObjectsRepository(driver)

        # <<<<<<<<<<<< Uncomment this code if choosing the Startingpoint and Destination from .env >>>>>>>
       
        # starting_point, destination_point = os.getenv("Startingpoint"), os.getenv("Destination")
        # if not starting_point or not destination_point: raise ValueError("Please set both 'Staringpoint' and 'Destination' environment variables.")
        # handle_got_it_popup(driver)
        # se_enter_text_and_select_suggestion(driver, repo.startingpoint, starting_point)
        # time.sleep(2)
        # se_enter_text_and_select_suggestion(driver, repo.destinationpoint, destination_point)
        # time.sleep(10)

        # <<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
       
        handle_got_it_popup(driver)

        se_wait_for_web_element(driver, 10, EC.presence_of_element_located(repo.leavenow))
        se_click_using_javascript(driver, driver.find_element(*repo.leavenow))
        time.sleep(3)
        se_click_dropdown_option_by_text(driver, "Arrive at", timeout=10)
        time.sleep(10)
        se_wait_for_web_element(driver, 10, EC.element_to_be_clickable(repo.arriveattime))
        # se_highlight_element(driver, driver.find_element(*repo.arriveattime))
        se_click_with_action_chain(driver, driver.find_element(*repo.arriveattime))
        
        
        se_wait_for_page_load(driver, timeout=100)
        export_dropdown_options_by_route(driver)

    except ValueError as ve: print(f"[ERROR] Environment variable issue: {ve}")
    except TimeoutException as te: print(f"[ERROR] Timeout while waiting for elements: {te}")
    except NoSuchElementException as ne: print(f"[ERROR] Element not found: {ne}")
    except Exception as e: print(f"[ERROR] Unexpected error occurred: {e}")
 

def print_dynamic_dropdown_options(driver):

    try:
        # Wait for dropdown to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wz-react-dropdown__list-container"))
        )

        dropdown = driver.find_element(By.CLASS_NAME, "wz-react-dropdown__list-container")
        options = dropdown.find_elements(By.XPATH, ".//div[normalize-space(text())!='']")

        print("Dropdown Options Found:")
        for index, opt in enumerate(options, start=1):
            text = opt.text.strip()
            if text:
                print(f"{index}. {text}")
            else:
                print(f"{index}. [Empty text or non-visible]")

    except Exception as e:
        print(f"Error fetching dropdown options: {e}")

def export_dropdown_options_by_route(driver):

    sheet_name = os.getenv("SHEET_NAME", "Traffic_Details")
    file_path = os.getenv("EXCEL_FILE", "default.xlsx")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wz-react-dropdown__list-container"))
        )

        dropdown = driver.find_element(By.CLASS_NAME, "wz-react-dropdown__list-container")
        total_options = dropdown.find_elements(By.XPATH, ".//div[normalize-space(text())!='']")
        # print(f"[DEBUG] Option  '{total_options}'")
        combined_data = []
        current_url = driver.current_url
        print(f"[DEBUG] Option  '{current_url}'")
        combined_data.insert(0, (f"URL: {current_url}", ""))
        for i in range(1,len(total_options)):
            # Re-fetch dropdown and options to avoid stale reference
            dropdown = driver.find_element(By.CLASS_NAME, "wz-react-dropdown__list-container")
            options = dropdown.find_elements(By.XPATH, ".//div[normalize-space(text())!='']")
            
            opt = options[i]
            # DEBUG: Print raw element and its text
            # print(f"[DEBUG] Option {i}: raw text = '{opt}'")

            time_text = opt.text.strip()
            if not time_text:
                continue

            estimated = get_estimated_time_on_hover(driver, opt)
            combined_data.append((time_text, estimated))
            # print(f"[INFO] Hovered Estimated Text: {time_text, estimated}")

        write_to_excel(sheet_name, combined_data, file_path)

    except Exception as e:
        print(f"Error fetching or writing dropdown options: {e}")
        traceback.print_exc()


def get_estimated_time_on_hover(driver, element, timeout=3):
        time.sleep(0.3)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        ActionChains(driver).move_to_element(element).perform()
        time.sleep(0.5)         
        # Extract estimated time from the text
        full_text = element.text.strip()
        # driver.execute_script("arguments[0].style = 'border:2px solid red; background-color:yellow; font-weight:bold;';", element)
        print(f"[DEBUG] Full element text: {full_text}")
        time.sleep(0.5) 
        match = re.search(r'(\d{1,2}:\d{2}\s*hr|\d+\s*hr|\d+\s*min)', full_text.lower())
        estimated_text = match.group(1) if match else ""

        return estimated_text
