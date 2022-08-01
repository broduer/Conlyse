from selenium.webdriver import DesiredCapabilities
import Bot.constants as const
from seleniumwire import webdriver
from Bot.login import Login
from Bot.scaper import WebScraper
from Bot.sort import sort
from Bot.sql.sql_filler import Filler
from time import sleep


options = webdriver.FirefoxOptions()
options.add_argument("--mute-audio")
# options.add_argument("--headless")
capabilities = DesiredCapabilities.FIREFOX


class Bot(webdriver.Firefox):
    def __init__(self, browser, teardown=True, firefox_options=options, desired_capabilities=capabilities):
        self.teardown = teardown
        self.browser = browser
        if browser:
            super(Bot, self).__init__(options=firefox_options, desired_capabilities=desired_capabilities)
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

    def scrap_static(self, botdata):
        return WebScraper(botdata, True).data

    def scrap_dynamic(self, botdata):
        return WebScraper(botdata, False).data

    def sort(self, game_id, data):
        self.sorted_data = sort(game_id, data).sorted_data
        return self.sorted_data

    def fillSQL(self, data):
        Filler(data)
