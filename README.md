

This project is a Python-based web scraping tool built using **Selenium**. It automates browser actions, extracts data, and writes the results to Excel.

---

##  Features

- Automated interaction with webpages using Selenium
- Extracts data via XPath and CSS selectors
- Handles dynamic content with wait conditions
- Saves data to Excel
- Uses utility modules for clean and reusable code

---

## Project Structure

```
Web-Scraper/
├── main.py                       # Entry point of the scraper
├── requirements.txt             # List of dependencies
├── utils/
│   ├── driver_context.py
│   ├── DriverFactory.py
│   ├── PageObjectsRepository.py
│   └── sleep_utils.py
├── excel_writer.py              # Excel writing utility
├── README.md                    # This file
```

---

## ⚙️ Setup Instructions

1. **Clone or Download this Repository**

   - If you received a `.zip`, extract it.
   -      cd web-scraper
     ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the Environment**

   - On **Windows CMD**:
     ```bash
     venv\Scripts\activate
     ```
   - On **Windows PowerShell**:
     ```bash
     .\venv\Scripts\Activate.ps1
     ```

4. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Scraper**

   ```bash
   python main.py
   ```


--
##  Notes

- ChromeDriver (or other browser drivers) must be compatible with your installed browser version.
- You can update the target URL and selectors inside your script or utility modules.

Get the compatible webdriver from internet

---


##  Update the .env File
Set the "BASE_URL" in the .env file.

Preferred: Use the complete search URL for direct navigation.

Alternative: If you want the script to simulate human typing for the starting point and destination, provide exact and valid location names.
BASE_URL=https://www.waze.com/
Startingpoint=Ohio Field
Destination= Lincoln Tunnel Weehawken Township, NJ, USA

This will allow the script to type into the search field and select the first suggested option as a human would. (Note: This method is not foolproof for selecting the exact location, as suggestions are influenced by the current geo-location.)

*****If you choose to use the starting point and destination method, make sure to uncomment the relevant block of code at the beginning of the navigate_to_map() function in the selenium_client.py file.


HEADLESS_DRIVER=True
Set this to True to run the browser in headless mode (i.e., without opening a visible browser window).



