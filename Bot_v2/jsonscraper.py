import json
import requests

headers = {
    "Accept": "text/plain, */*; q=0.01",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.conflictnations.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://www.conflictnations.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


class WebScraper():
    def __init__(self, loginData):
        self.loginData = loginData
        self.data = self.makeRequests()

    def makeRequests(self):
        response_data1 = requests.get(self.loginData["data_1"]["url"])
        response_data2 = requests.post(self.loginData["data_2"]["url"],
                                       headers=headers,
                                       data=self.loginData["data_2"]["body"])
        response_data3 = requests.post(self.loginData["data_3"]["url"],
                                       headers=headers,
                                       data=self.loginData["data_3"]["body"])
        if response_data1.status_code == 200 and response_data2.status_code == 200 and response_data3.status_code == 200:
            return [json.loads(response_data1.text), json.loads(response_data2.text), json.loads(response_data3.text)]
