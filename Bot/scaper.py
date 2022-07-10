import base64
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

header_data2 = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.conflictnations.com",
    "DNT": "1",
    "Referer": "https://www.conflictnations.com/",
}


class WebScraper:
    def __init__(self, botdata, static_request):
        self.botdata = botdata
        if static_request:
            self.data = self.make_static_request()
        else:
            self.data = self.make_dynamic_request()

    def make_static_request(self):
        data3_data = f"locale=en&units=1&upgrades=1&ranks=1&awards=1&mods=1&premiums=1&scenarios=1&title=1&researches=1&authTstamp={self.botdata['authTstamp']}&authUserID={self.botdata['siteUserID']}"
        response_1 = requests.get(self.botdata["urls"][0])
        response_3 = requests.post(self.botdata["urls"][2], headers=headers, data={
            "data": base64.b64encode(data3_data.encode("utf-8")).decode("utf-8")})
        if response_1.status_code == 200 and response_3.status_code == 200:
            return json.loads(response_1.text), json.loads(response_3.text)

    def make_dynamic_request(self):
        stateIDs = {"@c": "java.util.HashMap", **self.botdata["stateIDs"]} if "stateIDs" in self.botdata else {"@c": "java.util.HashMap"}
        tstamps = {"@c": "java.util.HashMap", **self.botdata["tstamps"]} if "tstamps" in self.botdata else {"@c": "java.util.HashMap"}
        data2_data = f'{{"requestID":1,"@c":"ultshared.action.UltUpdateGameStateAction","stateType":0,"stateID":"0","addStateIDsOnSent":true,"option":null,"actions":null,"lastCallDuration":0,"version":{self.botdata["version"]},"tstamps": {json.dumps(tstamps)}, "stateIDs": {json.dumps(stateIDs)}, "tstamp":"{self.botdata["tstamp"]}","client":"con-client","hash":"{self.botdata["hash"]}","sessionTstamp":0,"gameID":"{self.botdata["game_id"]}","playerID":{self.botdata["playerID"]},"siteUserID":"{self.botdata["siteUserID"]}","adminLevel":null,"rights":"chat","userAuth":"{self.botdata["userAuth"]}"}}'
        response_data2 = requests.post(self.botdata["urls"][1],
                                       data=data2_data)
        if response_data2.status_code == 200:
            return json.loads(response_data2.text)
