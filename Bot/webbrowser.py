import base64
import gzip
import json
from collections import Counter
from time import sleep
import logging

from constants import BOT_IP, SELENIUM_GRID_IP, SELENIUM_GRID_PORT, BROWSER_GAME_LOADING_TIMEOUT, BASE_URL

from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException

for log in ["seleniumwire", "hpack.hpack", "hpack.table", "urllib3.connectionpool",
            "selenium.webdriver.remote.remote_connection", "seleniumwire.server"]:
    logger = logging.getLogger(log)
    logger.setLevel(logging.CRITICAL + 1)


class Webbrowser(webdriver.Remote):
    def __init__(self, packet, teardown=True,
                 desired_capabilities=DesiredCapabilities.FIREFOX):
        self.data_requests = None
        self.teardown = teardown

        seleniumwire_options = {
            'suppress_connection_errors': False,
            'addr': BOT_IP,
        }
        try:
            if True:
                proxy_string = f'http://:{packet.local_ip}:{packet.local_port}'
                seleniumwire_options["proxy"] = {
                    'http': proxy_string,
                    'https': proxy_string,
                    'no_proxy': 'localhost,127.0.0.1'
                }
        except AttributeError:
            pass
        self.packet = packet

        super(Webbrowser, self).__init__(command_executor=f"http://{SELENIUM_GRID_IP}:{SELENIUM_GRID_PORT}",
                                         seleniumwire_options=seleniumwire_options,
                                         desired_capabilities=desired_capabilities)
        self.request_interceptor = self.interceptor
        self.implicitly_wait(15)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def run_game(self):
        self.login()
        self.join_game_round()
        data_requests = self.get_data_requests()
        return data_requests

    def run_game_list(self):
        self.login()
        self.click_new_games_tab()
        for i in range(50):
            self.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            sleep(0.2)
        sleep(5)
        return self.get_game_list_requests()

    def run_register_account(self):
        logging.debug("Requesting Login Page")
        self.get(BASE_URL)
        logging.debug("Login Page Loaded")
        if self.check_login_page():
            self.click_register_tab()
            self.type_registration_details()
            result = self.check_valid_register_inputs()
            self.wait_game_hub_page()
            return result
        return False

    def login(self):
        logging.debug("Requesting Login Page")
        self.get(BASE_URL)
        logging.debug("Login Page Loaded")
        if self.check_login_page():
            self.click_login_tab()
            self.type_login_credentials()
        self.wait_game_hub_page()

    def check_login_page(self):
        try:
            self.find_element(By.ID, "login-register-box")
            return True
        except NoSuchElementException:
            return False

    def wait_game_hub_page(self):
        try:
            WebDriverWait(self, BROWSER_GAME_LOADING_TIMEOUT).until(
                ec.frame_to_be_available_and_switch_to_it((By.ID, "ifm"))
            )
            WebDriverWait(self, BROWSER_GAME_LOADING_TIMEOUT).until(
                ec.presence_of_element_located((By.ID, "mainContent"))
            )
        except TimeoutException:
            logging.warning("Couldn't verify that cookies are set.")

    def type_login_credentials(self):
        logging.debug("Inserting Login Credentials")
        try:
            input_username_element = self.find_element(By.ID, "loginbox_login_input")
            input_password_element = self.find_element(By.ID, "loginbox_password_input")
            button_submit_element = self.find_element(By.CSS_SELECTOR, 'div[class="play-button"]')

            input_username_element.send_keys(self.packet.username)
            input_password_element.send_keys(self.packet.password)

            sleep(0.5)
            button_submit_element.click()
        except NoSuchElementException:
            logging.warning("Couldn't log into Account")

    def type_registration_details(self):
        logging.debug("Inserting Registration Details")
        try:
            input_username_element = self.find_element(By.ID, "username")
            input_password_element = self.find_element(By.ID, "password")
            input_email_element = self.find_element(By.ID, "email")

            input_username_element.send_keys(self.packet.username)
            input_password_element.send_keys(self.packet.password)
            input_email_element.send_keys(self.packet.email)

            sleep(2)
        except NoSuchElementException:
            logging.warning("Couldn't register Account")

    def check_valid_register_inputs(self):
        username_check_wrapper = self.find_element(By.ID, "sg_namecheck_wrapper")
        password_check_wrapper = self.find_element(By.ID, "sg_passwordcheck")
        email_check_wrapper = self.find_element(By.ID, "sg_emailcheck_wrapper")

        # Wrapper have class valid if they are valid
        username_classes = username_check_wrapper.get_attribute("class").split(" ")
        password_classes = password_check_wrapper.get_attribute("class").split(" ")
        email_classes = email_check_wrapper.get_attribute("class").split(" ")

        counter = Counter(username_classes + password_classes + email_classes)

        if counter["valid"] < 3:
            logging.warning("Inputs are invalid")
            return False
        else:
            button_submit_element = self.find_element(By.ID, 'func_ok_button')
            button_submit_element.click()
            return True

    def join_game_round(self):
        logging.debug("Joining Game")
        try:
            self.get(f"{BASE_URL}play.php?gameID={self.packet.game_id}")
        except Exception:
            logging.debug(f"ConnectError: {ConnectionError.args}")
        try:
            WebDriverWait(self, BROWSER_GAME_LOADING_TIMEOUT).until(
                ec.frame_to_be_available_and_switch_to_it((By.ID, "ifm"))
            )
            WebDriverWait(self, BROWSER_GAME_LOADING_TIMEOUT).until(
                ec.presence_of_element_located((By.ID, "layer3"))
            )
            logging.debug("Game loaded")
        except TimeoutException:
            logging.error("TimeoutException: Joining Game took to long.")

    def get_game_list_requests(self):
        game_list = []
        for request in self.requests:
            if request.response:
                if "https://www.conflictnations.com/index.php?eID=api&key=uberCon&action=getInternationalGames" \
                        in request.url:
                    self.wait_for_request(request.path)
                    try:
                        data = base64.b64decode(request.body.decode("utf-8")[4:]).decode("utf-8")
                    except UnicodeDecodeError:
                        continue
                    if "numEntriesPerPage" not in data:
                        continue
                    response_data = json.loads(gzip.decompress(request.response.body))
                    if "games" in response_data["result"]:
                        game_list += response_data["result"]["games"]
        return game_list

    def get_data_requests(self):
        data_requests = {}
        for request in self.requests:
            if request.response:
                try:
                    if "https://static1.bytro.com/fileadmin/mapjson/live" in request.url:
                        self.wait_for_request(request.path)
                        data_requests["1"] = {
                            "url": request.url,
                            "body": request.body.decode("utf-8"),
                            "data": json.loads(gzip.decompress(request.response.body)),
                        }

                    if "https://congs" in request.url:
                        self.wait_for_request(request.path)
                        body = json.loads(bytes.decode(request.body, "utf-8"))
                        if body["@c"] == "ultshared.action.UltUpdateGameStateAction" \
                                and body["requestID"] == 2 \
                                and self.packet.game_id == int(body['gameID']):
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
                except Exception:
                    logging.exception("Loading of Data failed")
        return data_requests

    def click_new_games_tab(self):
        try:
            close_button_modal = self.find_element(By.CSS_SELECTOR, 'div[class="func_close_button close_button_s"]')
            close_button_modal.click()
        except NoSuchElementException:
            logging.debug("Couldn't Close any disturbing windows")
        try:
            new_games_tab_element = self.find_element(By.ID, 'ui_open_new_games')
            new_games_tab_element.click()
        except NoSuchElementException:
            logging.warning("Couldn't log into Account")

    def click_login_tab(self):
        try:
            login_tab_element = self.find_element(By.CSS_SELECTOR, 'div[data-form="login"]')
            login_tab_element.click()
        except NoSuchElementException:
            logging.warning("Couldn't click Login Tab Button")

    def click_register_tab(self):
        try:
            register_tab_element = self.find_element(By.CSS_SELECTOR, 'div[data-form="register"]')
            register_tab_element.click()
        except NoSuchElementException:
            logging.warning("Couldn't click Register Tab Button")

    def interceptor(self, request):
        # Block PNG, JPEG and GIF images
        if request.path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ogg', '.webm', ".font")):
            request.abort()
