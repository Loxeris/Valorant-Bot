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

def getToken(cookies, username, password):
    url = "https://auth.riotgames.com/api/v1/authorization"

    payload = {
        "type": "auth",
        "username": username,
        "password": password,
        "remember": True,
        "language": "en_US"
    }
    headers = {"Content-Type": "application/json"}

    response = requests.put(url, json=payload, headers=headers, cookies=cookies)
    data = json.loads(response.content)
    try :
        token = data["response"]["parameters"]["uri"]
        token = token[token.find("token=")+6:token.find("&scope")]
        return token
    except :
        return None

def getEntitlement(riotToken):
    url = "https://entitlements.auth.riotgames.com/api/token/v1"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+ riotToken
    }
    response = requests.request("POST", url, headers=headers)
    data = json.loads(response.content)
    return data["entitlements_token"]

def getPuuidbyName(name):
    with open("puuid_list.json") as f:
        data = json.loads(f.read().lower())
        return data[name.lower()]

def getMatchID(puuid,riotToken,entitlement, region="eu"):
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
        print(data)
        return None

def fetchMatchPlayers(matchID,riotToken,entitlement, region="eu"):
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

def getVersion(puuid,riotToken,entitlement, region="eu"):
    url = f"https://glz-{region}-1.{region}.a.pvp.net/session/v1/sessions/f6f0b1d0-afd0-5619-95a6-3f677a7d715c"
    headers = {
        "X-Riot-Entitlements-JWT": entitlement,
        "Authorization": "Bearer "+ riotToken
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    print(data)
    return data["clientVersion"]

def fetchContent(clientPlatform,version,region="eu"):
    url = f"https://shared.{region}.a.pvp.net/content-service/v2/content"
    headers = {
        "X-Riot-ClientPlatform": clientPlatform,
        "X-Riot-ClientVersion": version
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    return data

def getCharacterName(CharID, content):
    for character in content["Characters"]:
        if character["ID"] == str.upper(CharID):
            return character["Name"]
    return "Character not found"

def getPlayerRank(puuid,riotToken,entitlement,clientPlatform,version,ranks, region='eu'):
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

def getPlayerStats(puuid,riotToken,entitlement,clientPlatform,version, region="eu"):
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

def getPlayerName(puuid,riotToken,entitlement, region="eu"):
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

def getUserPuuid(riotToken):
    url = "https://auth.riotgames.com/userinfo"
    headers = {
        "Authorization": "Bearer "+ riotToken,
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    return data["sub"]


def main(username, password):
    riotToken = getToken(getCookies(), username, password)

    if riotToken == None:
        return "Wrong Username and password combination"

    entitlement = getEntitlement(riotToken)
    userPuuid = getUserPuuid(riotToken)  # getPuuidbyName(name) #"9a4b2bdf-e43b-5893-8284-9759a4ec2fd1"
    clientPlatform = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
    ranks = {0:"Unranked", 3:"Iron 1",4:"Iron 2",5:"Iron 3", 6:"Bronze 1",7:"Bronze 2",8:"Bronze 3", 9:"Silver 1",10:"Silver 2",11:"Silver 3", 12:"Gold 1",13:"Gold 2",14:"Gold 3", 15:"Platinum 1",16:"Platinum 2",17:"Platinum 3", 18:"Diamond 1",19:"Diamond 2",20:"Diamond 3", 21:"Immortal 1",22:"Immortal 2",23:"Immortal 3", 24:"Radiant"}
    version = "release-03.04-shipping-15-598547"#getVersion(userPuuid, riotToken, entitlement)
    content = fetchContent(clientPlatform,version)
    


    if getMatchID(userPuuid, riotToken, entitlement)==None:
        return "The player is not in a match !"
    
    data = fetchMatchPlayers(getMatchID(userPuuid, riotToken, entitlement), riotToken, entitlement)

    blue = []
    red = []
    for player in data:
        if (player["TeamID"]=="Blue"):
            blue.append(player)
        else:
            red.append(player)
    text=""
    if (len(blue)==len(red)):
        for p1,p2 in zip(blue,red):
            stats1 = getPlayerStats(p1["Subject"],riotToken, entitlement, clientPlatform, version)
            stats2 = getPlayerStats(p2["Subject"],riotToken, entitlement, clientPlatform, version)
            text=(text +"{:<40}{:>40}".format("Defender " + getCharacterName(p1["CharacterID"],content) + f" [{getPlayerName(p1['Subject'],riotToken,entitlement)}] " + " : " , "Attacker " + getCharacterName(p2["CharacterID"],content) + f" [{getPlayerName(p2['Subject'],riotToken,entitlement)}] " + " :")+"\n")
            text=(text +"{:<40}{:>40}".format("LVL = "+str(p1["PlayerIdentity"]["AccountLevel"]) , "LVL = "+str(p2["PlayerIdentity"]["AccountLevel"]))+"\n")
            text=(text +"{:<40}{:>40}".format("Rank = " + getPlayerRank(p1["Subject"],riotToken,entitlement,clientPlatform,version,ranks) ,  "Rank = " + getPlayerRank(p2["Subject"],riotToken,entitlement,clientPlatform,version,ranks))+"\n")
            text=(text +"{:<40}{:>40}".format(f"ACS : {stats1['acs']}, Win % : {stats1['win%']} ({stats1['matchsNb']} matchs)" , f"ACS : {stats2['acs']}, Win % : {stats2['win%']} ({stats2['matchsNb']} matchs)")+"\n")
    else:        
        for player in data:
            stats = getPlayerStats(player["Subject"],riotToken, entitlement, clientPlatform, version)
            text=(text +("Defender " if player["TeamID"]=="Blue" else "Attacker ") + getCharacterName(player["CharacterID"],content) + f" [{getPlayerName(player['Subject'],riotToken,entitlement)}] " + " :"+"\n")
            text=(text +"    LVL = "+str(player["PlayerIdentity"]["AccountLevel"])+"\n")
            text=(text +"    Rank = " + getPlayerRank(player["Subject"],riotToken,entitlement,clientPlatform,version,ranks)+"\n")
            text=(text +f"    ACS : {stats['acs']}, Win % : {stats['win%']} (on last {stats['matchsNb']} matchs)"+"\n")
    print(text)
    print(len(text))
    return "```\n" + text + "\n```"
