from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


class PageObjectsRepository:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        
   
    @property
    def arriveattime(self):
        return (By.XPATH, "(//div[@class='wz-react-dropdown__head is-input'])[2]")
    
    @property
    def leavenow(self):
        return (By.XPATH, "//div[@class='wm-routing-schedule__icon']/following-sibling::div[@role='listbox']")
    
       
    @property
    def startingpoint(self):
        return (By.XPATH, "//div[@class='wz-search-container is-origin']//input[@class='wm-search__input']")
    
    @property
    def destinationpoint(self):
        return (By.XPATH, "//div[@class='wz-search-container is-destination']//input[@class='wm-search__input']")

        

    

