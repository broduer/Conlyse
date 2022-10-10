import base64
import gzip
import json
from time import sleep
import logging
from dotenv import load_dotenv
from os import getenv
from socket import gethostname, gethostbyname

from Networking.exceptions import GameJoinError
from Networking.packet_types import AccountRegisterRequest, GameDetail

from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver import DesiredCapabilities, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys

for log in ["seleniumwire", "hpack.hpack", "hpack.table", "urllib3.connectionpool",
            "selenium.webdriver.remote.remote_connection", "seleniumwire.server"]:
    logger = logging.getLogger(log)
    logger.setLevel(logging.CRITICAL + 1)

load_dotenv()


class Webbrowser(webdriver.Remote):
    def __init__(self, packet, teardown=True,
                 desired_capabilities=DesiredCapabilities.FIREFOX):
        self.data_requests = None
        self.teardown = teardown

        firefox_options = FirefoxOptions()
        # firefox_options.add_argument("--headless")

        # Disable images
        firefox_options.set_preference('permissions.default.image', 2)
        seleniumwire_options = {
            'addr': gethostbyname(gethostname()),
        }
        try:
            if packet.proxy_username and packet.proxy_password:
                proxy_string = f'socks5://{packet.proxy_username}:{packet.proxy_password}@{packet.local_ip}:{packet.local_port}'
                seleniumwire_options["proxy"] = {
                    'http': proxy_string,
                    'https': proxy_string,
                    'no_proxy': 'localhost,127.0.0.1'
                }
        except AttributeError:
            logging.warning("No Proxy")
        self.packet = packet

        super(Webbrowser, self).__init__(
            command_executor=f"http://{getenv('SELENIUM_GRID_IP')}:{getenv('SELENIUM_GRID_PORT')}",
            seleniumwire_options=seleniumwire_options,
            desired_capabilities=desired_capabilities,
            options=firefox_options)
        self.request_interceptor = self.interceptor
        self.implicitly_wait(5)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def run_game(self):
        self.login()
        self.wait_game_hub_page()
        joined = self.check_joined()
        if not joined:
            logging.debug("Needs to first time Join the Game")
            joined = self.join_game()
        else:
            self.get(f"{getenv('BASE_URL')}play.php?gameID={self.packet.game_id}")
        if joined:
            self.wait_game_round()
            self.select_random_country()
            data_requests = self.get_data_requests()
            return data_requests
        raise GameJoinError(f"Couldn't first time join Game {self.packet.game_id}")

    def run_game_list(self):
        self.login()
        self.wait_game_hub_page()
        self.click_new_games_tab()
        logging.debug("Scrolling to reveal all Games")
        for i in range(50):
            self.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            sleep(0.4)
        sleep(2)
        return self.get_game_list_requests()

    def run_register_account(self):
        logging.debug("Requesting Login Page")
        self.get(getenv('BASE_URL'))
        logging.debug("Login Page Loaded")
        if self.check_login_page():
            self.click_register_tab()
            self.type_registration_details()
            result = self.check_valid_register_inputs()
            if not result:
                return False
            self.wait_game_hub_page()
            return result
        return False

    def login(self):
        logging.debug("Requesting Login Page")
        self.get(getenv('BASE_URL'))
        logging.debug("Login Page Loaded")
        if self.check_login_page():
            self.click_login_tab()
            self.type_login_credentials()

    def check_joined(self):
        try:
            WebDriverWait(self, 3).until(
                ec.presence_of_element_located((By.XPATH, f'//button[@data-game-id="{self.packet.game_id}"]'))
            )
            return True
        except TimeoutException:
            return False

    def join_game(self):
        self.click_new_games_tab()
        try:
            WebDriverWait(self, int(getenv('BROWSER_VALIDATION_LOADING_TIMEOUT'))).until(
                ec.presence_of_element_located((By.XPATH, f'//div[@class="game-body game-info fb_top_right"]'))
            )
        except TimeoutException:
            pass
        try:
            search_box = self.find_element(By.ID, "searchUser")
            search_box.send_keys(self.packet.game_id)
            sleep(0.3)
            search_box.send_keys(Keys.ENTER)
        except NoSuchElementException:
            logging.debug("Couldn't find Search box")
            return False

        try:
            WebDriverWait(self, int(getenv('BROWSER_VALIDATION_LOADING_TIMEOUT'))).until(
                ec.presence_of_element_located((By.XPATH, f'//button[@data-game-id="{self.packet.game_id}"]'))
            ).click()
            WebDriverWait(self, int(getenv('BROWSER_VALIDATION_LOADING_TIMEOUT'))).until(
                ec.presence_of_element_located((By.XPATH, f'//button[@class="default_button func_confirm_dialog_accept"]'))
            ).click()
            return True
        except TimeoutException:
            logging.debug(f"Couldn't find Game Button for Game {self.packet.game_id}")
            return False

    def select_random_country(self):
        try:
            WebDriverWait(self, int(getenv('BROWSER_VALIDATION_LOADING_TIMEOUT'))).until(
                ec.presence_of_element_located((By.ID, "func_cat_chooser_random"))
            ).click()
        except TimeoutException:
            logging.debug("Couldn't select random Country")

    def check_login_page(self):
        try:
            self.find_element(By.ID, "login-register-box")
            return True
        except NoSuchElementException:
            return False

    def wait_game_hub_page(self):
        try:
            WebDriverWait(self, int(getenv('BROWSER_GAME_LOADING_TIMEOUT'))).until(
                ec.frame_to_be_available_and_switch_to_it((By.ID, "ifm"))
            )
            WebDriverWait(self, int(getenv('BROWSER_GAME_LOADING_TIMEOUT'))).until(
                ec.presence_of_element_located((By.ID, "mainContent"))
            )
            logging.debug("Game Hub Page Loaded")
            logging.debug("Closing any ADs")
            try:
                WebDriverWait(self, int(getenv('BROWSER_VALIDATION_LOADING_TIMEOUT'))).until(
                    ec.presence_of_element_located((By.XPATH, '//div[@class="func_close_button close_button_s"]'))
                ).click()
            except TimeoutException:
                logging.debug("No Ads found")
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

        except NoSuchElementException:
            logging.warning("Couldn't register Account")

    def check_valid_register_inputs(self):
        try:
            WebDriverWait(self, int(getenv('BROWSER_VALIDATION_LOADING_TIMEOUT'))).until(
                ec.presence_of_element_located((
                    By.XPATH, '//div[@id="sg_namecheck_wrapper" and contains(@class,"valid")]'))
            )
            WebDriverWait(self, int(getenv('BROWSER_VALIDATION_LOADING_TIMEOUT'))).until(
                ec.presence_of_element_located(
                    (By.XPATH, '//div[@id="sg_passwordcheck_wrapper" and contains(@class,"valid")]'))
            )
            WebDriverWait(self, int(getenv('BROWSER_VALIDATION_LOADING_TIMEOUT'))).until(
                ec.presence_of_element_located(
                    (By.XPATH, '//div[@id="sg_emailcheck_wrapper" and contains(@class,"valid")]'))
            )
        except TimeoutException:
            logging.warning("Inputs are invalid")
            return False
        try:
            WebDriverWait(self, int(getenv("BROWSER_VALIDATION_LOADING_TIMEOUT"))).until(
                ec.element_to_be_clickable((By.ID, 'func_ok_button'))
            )
            button_submit_element = self.find_element(By.ID, 'func_ok_button')
            button_submit_element.click()
        except TimeoutException:
            logging.debug("Couldn't click register button")
        return True

    def wait_game_round(self):
        try:
            WebDriverWait(self, int(getenv('BROWSER_GAME_LOADING_TIMEOUT'))).until(
                ec.frame_to_be_available_and_switch_to_it((By.ID, "ifm"))
            )
            WebDriverWait(self, int(getenv('BROWSER_GAME_LOADING_TIMEOUT'))).until(
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
            new_games_button = WebDriverWait(self, 3).until(
                ec.element_to_be_clickable((By.ID, 'ui_open_new_games'))
            )
            new_games_button.click()
            logging.debug("Clicked Open New Games Tab")
        except TimeoutException:
            logging.warning("Couldn't click new Games Tab")

    def click_login_tab(self):
        try:
            WebDriverWait(self, 10).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-form="login"]'))
            ).click()
        except TimeoutException:
            logging.warning("Couldn't click Login Tab Button")

    def click_register_tab(self):
        try:
            register_tab_element = self.find_element(By.CSS_SELECTOR, 'div[data-form="register"]')
            register_tab_element.click()
        except NoSuchElementException:
            logging.warning("Couldn't click Register Tab Button")

    def interceptor(self, request):
        # Block PNG, JPEG and GIF images
        if request.path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ogg', '.webm', ".font", ".svg", ".mp4",)):
            request.abort()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with Webbrowser(GameDetail(email="gfdgdfhdfg@gmail.com",
                               username="asdgsrds",
                               password="rSsUe3NXwzs56Md7",
                               local_ip="93.190.245.171",
                               local_port=9197,
                               server_uuid="sijdj>GIJsogkOKG",
                               account_id=23,
                               game_id=6206857,
                               joined=False)) as web:
        web.run_game()
