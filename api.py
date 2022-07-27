import requests, time
from datetime import datetime, date
from dateutil import parser

class valorant_api:

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False
        self.base_url = "https://api.henrikdev.xyz"
    
    def account_data(self, riot_username: str, riot_tag: str):
        r = self.session.get(self.base_url + "/valorant/v1/account/{}/{}".format(riot_username, riot_tag))
        if r.status_code != 200:
            return []
        data = r.json()["data"]
        puuid = data["puuid"]
        account_level = data["account_level"]
        region = data["region"]
        return [puuid, account_level, region]
    
    def check_rank(self, riot_username: str, riot_tag: str, region: str):
        r = self.session.get(
            self.base_url + "/valorant/v1/mmr/{}/{}/{}".format(region, riot_username, riot_tag)
        )
        if r.status_code != 200:
            return []
        data = r.json()["data"]
        rank_rating = data["mmr_change_to_last_game"]
        rank = data["currenttierpatched"]
        return [rank, rank_rating]
    
    def date_difference(self, date_1):
        today = str(date.today()).split(" ")[0]
        date1 = parser.parse(date_1)
        date2 = parser.parse(today)
        diff = date2 - date1
        return diff.days
    
    def last_game(self, riot_username: str, riot_tag: str, region: str):
        r = self.session.get(
            self.base_url + "/valorant/v1/mmr-history/{}/{}/{}".format(region, riot_username, riot_tag)
        )
        if r.status_code != 200:
            return []
        if r.json()["data"] == []:
            return []
        date_ts = str(datetime.fromtimestamp(r.json()["data"][0]["date_raw"])).split(" ")[0]
        last_played = self.date_difference(date_ts)
        return [last_played]
    
    def check_skins(self, entitlement_token: str, access_token: str, region: str, puuid: str):
        headers = {
            "X-Riot-Entitlements-JWT": entitlement_token,
            "Authorization": "Bearer {}".format(access_token)
        }
        check_url = "https://pd.{}.a.pvp.net/store/v1/entitlements/{}/e7c63390-eda7-46e0-bb7a-a6abdacd2433".format(region, puuid)
        api_skin_list_url = "https://raw.githubusercontent.com/useragents/Valorant-Account-Checker-with-Capture/main/skin_list.txt"
        user_skins = self.session.get(check_url, headers = headers).json()["Entitlements"]
        skin_list = self.session.get(api_skin_list_url).text.splitlines()
        skins = []
        for skin in user_skins: #Every skin the account has
            skin_id = skin["ItemID"]
            for line in skin_list:
                skin_name, api_skin_id = line.split("|")
                api_skin_id = api_skin_id.lower()
                try:
                    skin_name = skin_name.split(" Level")[0]
                except:
                    pass
                if api_skin_id == skin_id:
                    if "Standard" not in skin_name:
                        if "Melee" != skin_name:
                            skins.append(skin_name)
        return skins
