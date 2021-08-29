import time
import requests
import json


def getCookies():
    url = "https://auth.riotgames.com/api/v1/authorization"

    payload = {
        "client_id": "play-valorant-web-prod",
        "nonce": "1",
        "redirect_uri": "https://playvalorant.com/opt_in",
        "response_type": "token id_token"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.cookies

def getToken(cookies):
    url = "https://auth.riotgames.com/api/v1/authorization"

    payload = {
        "type": "auth",
        "username": "xBlackL0Lx",
        "password": "*loris*1",
        "remember": True,
        "language": "en_US"
    }
    headers = {"Content-Type": "application/json"}

    response = requests.put(url, json=payload, headers=headers, cookies=cookies)
    data = json.loads(response.content)
    token = data["response"]["parameters"]["uri"]
    token = token[token.find("token=")+6:token.find("&scope")]
    return token

riotToken = getToken(getCookies())

def getEntitlement():
    url = "https://entitlements.auth.riotgames.com/api/token/v1"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+ riotToken
    }
    response = requests.request("POST", url, headers=headers)
    data = json.loads(response.content)
    return data["entitlements_token"]

entitlement = getEntitlement()

def getPuuidbyName(name):
    with open("puuid_list.json") as f:
        data = json.loads(f.read().lower())
        return data[name.lower()]

userPuuid = getPuuidbyName("Loxeris#EEB") #"9a4b2bdf-e43b-5893-8284-9759a4ec2fd1"
clientPlatform = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"

ranks = {0:"Unranked", 3:"Iron 1",4:"Iron 2",5:"Iron 3", 6:"Bronze 1",7:"Bronze 2",8:"Bronze 3", 9:"Silver 1",10:"Silver 2",11:"Silver 3", 12:"Gold 1",13:"Gold 2",14:"Gold 3", 15:"Platinum 1",16:"Platinum 2",17:"Platinum 3", 18:"Diamond 1",19:"Diamond 2",20:"Diamond 3", 21:"Immortal 1",22:"Immortal 2",23:"Immortal 3", 24:"Radiant"}

def getMatchID(region="eu", puuid=userPuuid):
    url = f"https://glz-{region}-1.{region}.a.pvp.net/core-game/v1/players/{puuid}"
    headers = {
        "X-Riot-Entitlements-JWT": entitlement,
        "Authorization": "Bearer "+ riotToken
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    try :
        return data["MatchID"]
    except:
        return None

def fetchMatchPlayers(matchID, region="eu"):
    if matchID==None :
        return None
    
    url=f"https://glz-{region}-1.{region}.a.pvp.net/core-game/v1/matches/{matchID}"
    headers = {
        "X-Riot-Entitlements-JWT": entitlement,
        "Authorization": "Bearer "+ riotToken
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    try:
        return data["Players"]
    except:
        return None

def getVersion(region="eu", puuid=userPuuid):
    url = f"https://glz-{region}-1.{region}.a.pvp.net/session/v1/sessions/{puuid}"
    headers = {
        "X-Riot-Entitlements-JWT": entitlement,
        "Authorization": "Bearer "+ riotToken
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    return data["clientVersion"]

version = getVersion()


def fetchContent(region="eu"):
    url = f"https://shared.{region}.a.pvp.net/content-service/v2/content"
    headers = {
        "X-Riot-ClientPlatform": clientPlatform,
        "X-Riot-ClientVersion": version
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    return data

content = fetchContent()

def getCharacterName(CharID, content=content):
    for character in content["Characters"]:
        if character["ID"] == str.upper(CharID):
            return character["Name"]
    return "Character not found"

def getPlayerRank(puuid, region='eu'):
    url = f"https://pd.{region}.a.pvp.net/mmr/v1/players/{puuid}"
    headers = {
        "X-Riot-Entitlements-JWT": entitlement,
        "Authorization": "Bearer "+ riotToken,
        "X-Riot-ClientPlatform": clientPlatform,
        "X-Riot-ClientVersion": version
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    try:
        return ranks[data["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]["2a27e5d2-4d30-c9e2-b15a-93b8909a442c"]["CompetitiveTier"]]
    except:
        return "Unranked"

def getPlayerStats(puuid, region="eu"):
    wins = 0
    matchsNb = 0
    acs = 0
    REQUESTMATCHNB = 5

    url = f"https://pd.{region}.a.pvp.net/match-history/v1/history/{puuid}?queue=competitive&endIndex={REQUESTMATCHNB}"
    headers = {
        "X-Riot-Entitlements-JWT": entitlement,
        "Authorization": "Bearer "+ riotToken,
        "X-Riot-ClientPlatform": clientPlatform,
        "X-Riot-ClientVersion": version
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    for match in data["History"]:
        url = f"https://pd.{region}.a.pvp.net/match-details/v1/matches/{match['MatchID']}"
        headers = {
            "X-Riot-Entitlements-JWT": entitlement,
            "Authorization": "Bearer "+ riotToken,
            "X-Riot-ClientPlatform": clientPlatform,
            "X-Riot-ClientVersion": version
        }
        response = requests.get(url, headers=headers)
        matchdata = json.loads(response.content)

        matchsNb+=1
        
        for team in matchdata["teams"]:
            if team["teamId"]==match["TeamID"]:
                if team["won"]:
                    wins+=1

        for player in matchdata["players"]:
            if player["subject"]==puuid:
                acs += player["stats"]["score"]//player["stats"]["roundsPlayed"]

    if matchsNb!=REQUESTMATCHNB:
        url = f"https://pd.{region}.a.pvp.net/match-history/v1/history/{puuid}?queue=unrated&endIndex={REQUESTMATCHNB-matchsNb}"
        headers = {
            "X-Riot-Entitlements-JWT": entitlement,
            "Authorization": "Bearer "+ riotToken,
            "X-Riot-ClientPlatform": clientPlatform,
            "X-Riot-ClientVersion": version
        }
        response = requests.get(url, headers=headers)
        data = json.loads(response.content)
        for match in data["History"]:
            url = f"https://pd.{region}.a.pvp.net/match-details/v1/matches/{match['MatchID']}"
            headers = {
                "X-Riot-Entitlements-JWT": entitlement,
                "Authorization": "Bearer "+ riotToken,
                "X-Riot-ClientPlatform": clientPlatform,
                "X-Riot-ClientVersion": version
            }
            response = requests.get(url, headers=headers)
            matchdata = json.loads(response.content)

            matchsNb+=1
            
            for team in matchdata["teams"]:
                if team["teamId"]==match["TeamID"]:
                    if team["won"]:
                        wins+=1

            for player in matchdata["players"]:
                if player["subject"]==puuid:
                    acs += player["stats"]["score"]//player["stats"]["roundsPlayed"]
    if matchsNb==0:
        return {"win%":"No data", "acs":"No data", "matchsNb":matchsNb}
    return {"win%":wins/matchsNb*100, "acs":acs//matchsNb, "matchsNb":matchsNb}

def getPlayerName(puuid, region="eu"):
    url = f"https://pd.{region}.a.pvp.net/name-service/v2/players"
    headers = {
        "X-Riot-Entitlements-JWT": entitlement,
        "Authorization": "Bearer "+ riotToken,
        "Content-Type": "application/json"
    }
    content = [puuid]
    response = requests.put(url, json=content, headers=headers)
    data = json.loads(response.content)
    return data[0]["GameName"]





print("Waiting for a match...\n")
while(getMatchID()==None):
    time.sleep(5)
print("Match found ! Fetching data...\n")
data = fetchMatchPlayers(getMatchID())

blue = []
red = []
for player in data:
    if (player["TeamID"]=="Blue"):
        blue.append(player)
    else:
        red.append(player)
if (len(blue)==len(red)):
    for p1,p2 in zip(blue,red):
        stats1 = getPlayerStats(p1["Subject"])
        stats2 = getPlayerStats(p2["Subject"])
        print ("{:<70}{:>70}".format("Defender " + getCharacterName(p1["CharacterID"]) + f" [{getPlayerName(p1['Subject'])}] " + " : " , "Attacker " + getCharacterName(p2["CharacterID"]) + f" [{getPlayerName(p2['Subject'])}] " + " :"))
        print("{:<70}{:>70}".format("LVL = "+str(p1["PlayerIdentity"]["AccountLevel"]) , "LVL = "+str(p2["PlayerIdentity"]["AccountLevel"])))
        print("{:<70}{:>70}".format("Rank = " + getPlayerRank(p1["Subject"]) ,  "Rank = " + getPlayerRank(p2["Subject"])))
        print("{:<70}{:>70}".format(f"ACS : {stats1['acs']}, Win % : {stats1['win%']} (on last {stats1['matchsNb']} matchs)" , f"ACS : {stats2['acs']}, Win % : {stats2['win%']} (on last {stats2['matchsNb']} matchs)"))
        print("")
else:        
    for player in data:
        stats = getPlayerStats(player["Subject"])
        print (("Defender " if player["TeamID"]=="Blue" else "Attacker ") + getCharacterName(player["CharacterID"]) + f" [{getPlayerName(player['Subject'])}] " + " :")
        print("    LVL = "+str(player["PlayerIdentity"]["AccountLevel"]))
        print("    Rank = " + getPlayerRank(player["Subject"]))
        print(f"    ACS : {stats['acs']}, Win % : {stats['win%']} (on last {stats['matchsNb']} matchs)")
        print("")

