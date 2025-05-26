import requests
import pandas as pd
import dotenv

config = dotenv.dotenv_values('.env')
token = config['token']
request_url = config['request_url']
make_requests = (config['make_requests'] == 'True')
save_info = (config['save_info'] == 'True')

def make_request_teams():
    if not make_requests:
        return None
    response = requests.get(request_url + "/teams", headers={"Authorization": token})
    if not response.ok:
        return None
    teams = response.json()
    teams = pd.DataFrame(teams)
    return teams

def make_request_players(players_id):
    if not make_requests:
        return None
    players = pd.DataFrame({"id": [], "name": [], "surname": [], "number": []})
    for id in players_id:
        response = requests.get(request_url + "/players/" + str(id), headers={"Authorization": token})
        if not response.ok:
            return None
        player = response.json()
        players.loc[len(players)] = player
    return players
        
def make_request_matches():
    if not make_requests:
        return None
    response = requests.get(request_url + "/matches", headers={"Authorization": token})
    if not response.ok:
        return None
    matches = response.json()
    matches = pd.DataFrame(matches)
    return matches

def init():
    teams = make_request_teams()
    if type(teams) != pd.DataFrame:
        teams = pd.read_csv('teams.csv')
    elif save_info:
        teams.to_csv('teams.csv')

    matches = make_request_matches()
    if type(matches) != pd.DataFrame:
        matches = pd.read_csv('matches.csv')
    elif save_info:
        matches.to_csv('matches.csv')

    players_id = []
    for lst in teams['players']:
        for x in lst:
            players_id.append(x)
    players_id.sort()
    players_id = list(dict.fromkeys(players_id))
    players = make_request_players(players_id)
    if type(players) != pd.DataFrame:
        players = pd.read_csv('players.csv')
    elif save_info:
        players.to_csv('players.csv')

    return teams, matches, players

teams, matches, players = init()


def print_players():
    """Вывести список игроков в консоль"""
    for i in range(len(players)):
        print(players['name'][i], players['surname'][i])

def get_request():
    request = input().split(maxsplit=1)
    if request[0] == "exit":
        return "exit", []
    elif request[0] == "stats?":
        return "stats", [request[1][1:-1]]
    elif request[0] == "versus?":
        request[1] = request[1].split()
        return "versus", [int(request[1]), int(request[2])]

def stats(team_name):
    """Возвращает статистику по команде (количество побед, поражений, разница забитых и пропущенных голов)"""
    if len(teams[teams['name'] == team_name]) == 0:
        return 0, 0, 0
    team_id = list(teams[teams['name'] == team_name]['id'])[0]
    wins = len(matches[(matches['team1'] == team_id) & (matches['team1_score'] > matches['team2_score'])])\
        + len(matches[(matches['team2'] == team_id) & (matches['team1_score'] < matches['team2_score'])])
    losings = len(matches[(matches['team1'] == team_id) & (matches['team1_score'] < matches['team2_score'])])\
        + len(matches[(matches['team2'] == team_id) & (matches['team1_score'] > matches['team2_score'])])
    goals = matches[matches['team1'] == team_id]['team1_score'].sum() + matches[matches['team2'] == team_id]['team2_score'].sum()\
        - matches[matches['team2'] == team_id]['team1_score'].sum() - matches[matches['team1'] == team_id]['team2_score'].sum()
    return wins, losings, int(goals)

def versus():
    return

if __name__ == "__main__":
    print_players()
    while True:
        request_type, params = get_request()
        if request_type == "exit":
            break
        elif request_type == "stats":
            wins, losings, goals = stats(params[0])
            print(wins, losings, goals)

