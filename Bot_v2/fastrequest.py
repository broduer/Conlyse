import json

import requests


class fastrequest:
    def __init__(self, logindata):
        self.data = self.makeRequest(logindata)

    def makeRequest(self, logindata):
        url = logindata["url"]
        tstamp = logindata["tstamp"]
        version = logindata["version"]
        hash = logindata["hash"]
        game_id = logindata["game_id"]
        player_id = logindata["player_id"]
        site_user_id = logindata["site_user_id"]
        user_auth = logindata["user_auth"]
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

        data = {
            "requestID": 2,
            "@c": "ultshared.action.UltUpdateGameStateAction",
            "stateType": 0,
            "stateID": "0",
            "addStateIDsOnSent": True,
            "option": None,
            "actions":
                [
                    "java.util.LinkedList",
                    [
                        {
                            "requestID": "actionReq-1",
                            "@c": "ultshared.action.UltLoginAction",
                            "resolution": "1920x1080",
                            "sysInfos":
                                {
                                    "@c": "ultshared.action.UltSystemInfos",
                                    "verbose": False,
                                    "clientVersion": version,
                                    "processors": "",
                                    "accMem": "",
                                    "javaVersion": "",
                                    "osArch": "",
                                    "osName": "",
                                    "osVersion": "",
                                    "osPatchLevel": "",
                                    "userCountry": "",
                                    "screenWidth": 1920,
                                    "screenHeight": 1080
                                }
                        }
                    ]
                ],
            "lastCallDuration": 0,
            "version": version,
            "tstamp": tstamp,
            "client": "con-client",
            "hash": hash,
            "sessionTstamp": 0,
            "gameID": game_id,
            "playerID": player_id,
            "siteUserID": site_user_id,
            "adminLevel": None,
            "rights": "chat",
            "userAuth": user_auth,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = json.loads(response.text)
        if response_json.get("result").get("@c") == "ultshared.rpc.UltSwitchServerException":
            logindata["url"] = f"https://{response_json.get('result').get('newHostName')}/"
            with open(f"fastlogin_{logindata['game_id']}.json", "w") as file:
                file.write(json.dumps(logindata, indent=2))
            response_json = self.makeRequest(logindata)
        return response_json
