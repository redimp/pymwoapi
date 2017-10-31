#!/usr/bin/env python

import requests
from pprint import pprint

def _fetch_game_json(key, id):
    # build url
    url = "https://mwomercs.com/api/v1/matches/{0}?api_token={1}".format(id, key)
    # requests data
    response = requests.get(url)
    # convert into json
    data = response.json()
    # error handling
    if not response.ok:
        # unfortunaley does pgi use both 'error' and 'message' to deliver
        # error messages
        if 'error' in data:
            message = "Error {0}: {1}".format(data['status'], data['error'])
        elif 'message' in data:
            message = "Error {0}: {1}".format(data['status'], data['message'])
        else:
            message = "Unknown Error"
        raise RuntimeError(message)
    # everything is fine, return data
    return data, response.headers

def fetch_game(key, id):
    data, headers = _fetch_game_json(key, id)
    # handle gamedata
    g = Game(id)
    # set gamedata
    g.map = data[u'MatchDetails'][u'Map']
    g.completetime = data[u'MatchDetails'][u'CompleteTime']
    g.gamemode = data[u'MatchDetails'][u'GameMode']
    g.matchduration = int(data[u'MatchDetails'][u'MatchDuration'])
    g.matchtimeminutes = int(data[u'MatchDetails'][u'MatchTimeMinutes'])
    g.nomechefficiencies = data[u'MatchDetails'][u'NoMechEfficiencies']
    g.nomechquirks = data[u'MatchDetails'][u'NoMechQuirks']
    g.region = data[u'MatchDetails'][u'Region']
    g.team1score = int(data[u'MatchDetails'][u'Team1Score'])
    g.team2score = int(data[u'MatchDetails'][u'Team2Score'])
    g.timeofday = data[u'MatchDetails'][u'TimeOfDay']
    g.usestockloadout = data[u'MatchDetails'][u'UseStockLoadout']
    g.viewmode = data[u'MatchDetails'][u'ViewMode']
    g.winningteam = int(data[u'MatchDetails'][u'WinningTeam'])
    # set winner and looser
    if g.winningteam == 1:
        g.winner = g.team1
        g.looser = g.team2
    else:
        g.winner = g.team2
        g.looser = g.team1

    # collect player data
    for udata in data[u'UserDetails']:
        p = Player()
        p.assists = udata[u'Assists']
        p.componentsdestroyed = udata[u'ComponentsDestroyed']
        p.damage = udata[u'Damage']
        p.healthpercentage = udata[u'HealthPercentage']
        p.isspectator = udata[u'IsSpectator']
        p.kills = udata[u'Kills']
        p.killsmostdamage = udata[u'KillsMostDamage']
        p.lance = udata[u'Lance']
        p.matchscore = udata[u'MatchScore']
        p.mechitemid = udata[u'MechItemID']
        p.mechname = udata[u'MechName']
        p.skilltier = udata[u'SkillTier']
        p.team = int(udata[u'Team'])
        p.teamdamage = udata[u'TeamDamage']
        p.unittag = udata[u'UnitTag']
        p.username = udata[u'Username']

        # add player to either spectator, team 1 or 2
        if p.isspectator:
            g.spectator.append(p)
        elif p.team == 1:
            g.team1.append(p)
        else:
            g.team2.append(p)

    return g

class Game(object):
    def __init__(self, gameid):
        self.gameid = gameid
        self.team1 = []
        self.team2 = []
        self.spectator = []
        self.winner = None
        self.looser = None
        self.completetime = None
        self.gamemode = None
        self.map = None
        self.matchduration = None
        self.matchtimeminutes = None
        self.nomechefficiencies = None
        self.nomechquirks = None
        self.region = None
        self.team1score = None
        self.team2score = None
        self.timeofday = None
        self.usestockloadout = None
        self.viewmode = None
        self.winningteam = None

    def __repr__(self):
        return "<Game {0}>".format(self.gameid)

class Player(object):
    def __init__(self):
        self.assists = None
        self.componentsdestroyed = None
        self.damage = None
        self.healthpercentage = None
        self.isspectator = None
        self.kills = None
        self.killsmostdamage = None
        self.lance = None
        self.matchscore = None
        self.mechitemid = None
        self.mechname = None
        self.skilltier = None
        self.team = None
        self.teamdamage = None
        self.unittag = None
        self.username = None

    def __repr__(self):
        return "<Player '{0}'>".format(self.username)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="Verbose mode", action="store_true")
    parser.add_argument("key", help="Secret Key. Get it from https://mwomercs.com/profile/api", 
            type=str)
    parser.add_argument("id", help="game-ids as displayed", type=str, nargs="+")
    # parse args
    args = parser.parse_args()

    # we enable requests_cache to avoid running into X-RateLimits
    import requests_cache
    requests_cache.install_cache('mwoapicache', backend='sqlite', expire_after=3600)

    # check every game-id
    for gid in args.id:
        try:
            g = fetch_game(args.key, gid)
        except RuntimeError as e:
            print e
            continue
        print "Mode: {0}   Map: {1}   Time: {2}".format(g.gamemode, g.map, g.completetime)
        for p in g.winner:
            print "{0:20.20} {1:4}  {2:2}  {3:2}  {4:2}  {5:4}  {6:4}".format(
                    p.username, p.unittag, p.kills, p.killsmostdamage,
                    p.assists, p.damage, p.matchscore)
        for p in g.looser:
            print "{0:20.20} {1:4}  {2:2}  {3:2}  {4:2}  {5:4}  {6:4}".format(
                    p.username, p.unittag, p.kills, p.killsmostdamage,
                    p.assists, p.damage, p.matchscore)
