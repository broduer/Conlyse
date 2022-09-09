import base64
import gzip
import json
import os
from time import sleep
import logging

import constants as const

from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from selenium.common import exceptions

for log in ["seleniumwire", "hpack.hpack", "hpack.table", "urllib3.connectionpool",
            "selenium.webdriver.remote.remote_connection"]:
    logger = logging.getLogger(log)
    logger.setLevel(logging.ERROR)

seleniumwire_options = {
    "enable_har": False
}

options = webdriver.FirefoxOptions()
options.add_argument("--mute-audio")
# options.add_argument("--headless")
capabilities = DesiredCapabilities.FIREFOX
capabilities["pageLoadStrategy"] = "eager"  # interactive


class Webbrowser(webdriver.Firefox):
    def __init__(self, login_data, teardown=True, firefox_options=options, desired_capabilities=capabilities):
        self.data_requests = None
        self.login_data = login_data
        self.teardown = teardown
        super(Webbrowser, self).__init__(service_log_path=os.path.devnull, seleniumwire_options=seleniumwire_options,
                                         options=firefox_options, capabilities=desired_capabilities)
        # self.request_interceptor = self.interceptor

        self.implicitly_wait(15)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def interceptor(self, request):
        # Block PNG, JPEG and GIF images
        if request.path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ogg', '.webm', ".font")):
            request.abort()

    def check_login_page(self):
        try:
            self.find_element(By.ID, "login-register-box")
            return True
        except exceptions.NoSuchElementException:
            return False

    def wait_game_hub_page(self):
        try:
            WebDriverWait(self, const.BROWSER_GAME_LOADING_TIMEOUT).until(
                ec.frame_to_be_available_and_switch_to_it((By.ID, "ifm"))
            )
            WebDriverWait(self, const.BROWSER_GAME_LOADING_TIMEOUT).until(
                ec.presence_of_element_located((By.ID, "mainContent"))
            )
        except exceptions.TimeoutException:
            logging.warning("Couldn't verify that cookies are set.")

    def click_tab(self):
        try:
            login_tab_element = self.find_element(By.CSS_SELECTOR, 'div[data-form="login"]')
            login_tab_element.click()
        except exceptions.NoSuchElementException:
            logging.warning("Couldn't log into Account")

    def type_login_credentials(self):
        logging.debug("Inserting Login Credentials")
        try:
            input_username_element = self.find_element(By.ID, "loginbox_login_input")
            input_password_element = self.find_element(By.ID, "loginbox_password_input")
            button_submit_element = self.find_element(By.CSS_SELECTOR, 'div[class="play-button"]')

            input_username_element.send_keys(self.login_data["bot_username"])
            input_password_element.send_keys(self.login_data["bot_password"])

            sleep(0.5)
            button_submit_element.click()
        except exceptions.NoSuchElementException:
            logging.warning("Couldn't log into Account")

    def join_game_round(self):
        logging.debug("Joining Game")
        self.get(f"{const.BASE_URL}play.php?gameID={self.login_data['game_id']}")
        try:
            WebDriverWait(self, const.BROWSER_GAME_LOADING_TIMEOUT).until(
                ec.frame_to_be_available_and_switch_to_it((By.ID, "ifm"))
            )
            WebDriverWait(self, const.BROWSER_GAME_LOADING_TIMEOUT).until(
                ec.presence_of_element_located((By.ID, "layer3"))
            )
            logging.debug("Game loaded")
        except exceptions.TimeoutException:
            logging.error("TimeoutException: Joining Game took to long.")

    def get_data_requests(self):
        data_requests = {}
        for request in self.requests:
            if request.response:
                try:
                    if "https://static1.bytro.com/fileadmin/mapjson/live" in request.url:
                        self.wait_for_request(request.path)
                        data_requests["1"] = {
                            "url": request.url,
                            "body": bytes.decode(request.body, "utf-8"),
                            "data": json.loads(gzip.decompress(request.response.body)),
                        }

                    if "https://congs" in request.url:
                        self.wait_for_request(request.path)
                        body = json.loads(bytes.decode(request.body, "utf-8"))
                        if body["@c"] == "ultshared.action.UltUpdateGameStateAction" \
                                and body["requestID"] == 2 \
                                and self.login_data["game_id"] == body['gameID']:
                            data_requests["2"] = {
                                "url": request.url,
                                "body": body,
                                "data": json.loads(gzip.decompress(request.response.body)),
                            }

                    if "https://www.conflictnations.com/index.php?eID=api&key=ingameCon&action=getContentItems" in request.url:
                        self.wait_for_request(request.path)
                        data_requests["3"] = {
                            "url": request.url,
                            "body": base64.b64decode(bytes.decode(request.body)[5:]).decode("utf-8"),
                            "data": json.loads(gzip.decompress(request.response.body)),
                        }
                except:
                    logging.exception("Loading of Data failed")
        return data_requests

    def run(self):
        logging.debug("Requesting Login Page")
        self.get(const.BASE_URL)
        logging.debug("Login Page Loaded")
        if self.check_login_page():
            self.click_tab()
            self.type_login_credentials()
        self.wait_game_hub_page()
        self.join_game_round()
        data_requests = self.get_data_requests()
        return data_requests
