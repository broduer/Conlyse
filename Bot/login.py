import base64
import re
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

import json


class Login:
    def __init__(self, driver: webdriver, bot_data):
        self.driver = driver
        self.bot_data = bot_data
        if self.checkLoginPage():
            self.clickTab()
            self.typeData()
            self.submit()
            self.join()
            self.log = self.getLog()
            self.data_url = [self.getUrl(1, self.log), self.getUrl(2, self.log), self.getUrl(3, self.log)]
            self.data_2 = self.getData_2()
            self.data_3 = self.getData_3()
            self.loginData = self.getLoginData()

    def checkLoginPage(self):
        try:
            self.driver.find_element(By.ID, "login-register-box")
            return True
        except:
            return False

    def clickTab(self):
        login_tab_element = self.driver.find_element(By.CSS_SELECTOR, 'div[data-form="login"]')
        login_tab_element.click()

    def typeData(self):
        input_username_element = self.driver.find_element(By.ID, "loginbox_login_input")
        input_password_element = self.driver.find_element(By.ID, "loginbox_password_input")

        input_username_element.send_keys(self.bot_data["bot_username"])
        input_password_element.send_keys(self.bot_data["bot_password"])

    def submit(self):
        button_submit_element = self.driver.find_element(By.CSS_SELECTOR, 'div[class="play-button"]')
        button_submit_element.click()

    def join(self):
        sleep(3)
        self.driver.get(f"https://www.conflictnations.com/play.php?gameID={self.bot_data['game_id']}")
        WebDriverWait(self.driver, 15).until(
            ec.frame_to_be_available_and_switch_to_it((By.ID, "ifm"))
        )
        WebDriverWait(self.driver, 15).until(
            ec.presence_of_element_located((By.ID, "layer3"))
        )
        sleep(5)

    def getLoginData(self):
        loginData = dict(
            {
                "game_id": self.data_2["gameID"],
                "version": self.data_2["version"],
                "urls": self.data_url,
                "hash": self.data_2["hash"],
                "playerID": self.data_2["playerID"],
                "siteUserID": self.data_2["siteUserID"],
                "tstamp": self.data_2["tstamp"],
                "authTstamp": re.findall("(?<=authTstamp=)[0-9]{10}", self.data_3)[0],
                "userAuth": self.data_2["userAuth"],
            }
        )
        return loginData

    def getLog(self):
        return self.driver.get_log("performance")

    def getUrl(self, number, logs_raw):
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
        if number == 1:
            for log in filter(self.log_filter_1, logs):
                return log["params"]["request"]["url"].split("?")[0]
        elif number == 2:
            for request in self.driver.requests:
                if request.response:
                    if "https://congs" in request.url:
                        return request.url
        elif number == 3:
            for request in self.driver.requests:
                if request.response:
                    if "https://www.conflictnations.com/index.php?eID=api&key=ingameCon&action=getContentItems" in request.url:
                        return request.url

    def log_filter_1(self, log_):
        return (
            # is an actual response
                log_["method"] == "Network.requestWillBeSent"
                # and json
                and "https://static1.bytro.com/fileadmin/mapjson/live" in log_["params"]["request"]["url"]
        )

    def getData_2(self):
        for request in self.driver.requests:
            if request.response:
                if "https://congs" in request.url:
                    try:
                        body = json.loads(bytes.decode(request.body))
                        if body["@c"] == "ultshared.action.UltUpdateGameStateAction":
                            return body
                    except:
                        pass

    def getData_3(self):
        for request in self.driver.requests:
            if request.response:
                if "https://www.conflictnations.com/index.php?eID=api&key=ingameCon&action=getContentItems" in request.url:
                    try:
                        body = bytes.decode(request.body)
                        if "data" in body:
                            print(body)
                            return base64.b64decode(body[5:]).decode("utf-8")
                    except:
                        pass
