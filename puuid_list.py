import json
import ssl
import requests
import os

puuid_list = {}

with open("puuid_list.json") as f:
    data = json.load(f)
    for a in data:
        puuid_list[a] = data[a]

############################### GET FRIENDS PUUIDS ##################################
lockfile = "".join(
    [os.getenv("LOCALAPPDATA"), r"\Riot Games\Riot Client\Config\lockfile"]
)

with open(lockfile, "r") as f:
    data = f.read().split(":")

base_url = f"{data[4]}://127.0.0.1:{data[2]}"
s = requests.Session()
s.auth = ("riot", data[3])
def url(path):
    return base_url+path

response = s.get(url("/chat/v4/friends"), verify=ssl.CERT_NONE)
data = json.loads(response.content)
for friend in data["friends"]:
    puuid_list[f'{friend["game_name"]}#{friend["game_tag"]}'] = friend["puuid"]

###################################################################################

with open("puuid_list.json", "w+") as f:
    f.write(json.dumps(puuid_list))

    