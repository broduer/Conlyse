from selenium.webdriver import DesiredCapabilities
import Bot_v2.constants as const
from seleniumwire import webdriver
from Bot_v2.login import Login
from Bot_v2.jsonscraper import WebScraper
from Bot_v2.sort import sort
from Bot_v2.sql.sql_filler import Filler
from time import sleep


options = webdriver.ChromeOptions()
options.add_argument("--mute-audio")
options.add_argument("--headless")
capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+


class Bot(webdriver.Chrome):
    def __init__(self, browser, teardown=True, chrome_options=options, desired_capabilities=capabilities):
        self.teardown = teardown
        self.browser = browser
        if browser:
            super(Bot, self).__init__(chrome_options=chrome_options, desired_capabilities=desired_capabilities)
            self.implicitly_wait(15)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            sleep(1)
            if self.browser:
                self.quit()

    def land_first_page(self):
        self.get(const.BASE_URL)

    def loginBot(self, bot_data):
        return Login(self, bot_data).loginData

    def scrap(self, loginData):
        return WebScraper(loginData).data

    def sort(self, data):
        self.sorted_data = sort(data).sorted_data
        return self.sorted_data

    def fillSQL(self, data):
        Filler(data)
