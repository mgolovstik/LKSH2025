import requests
import pandas as pd
import dotenv

config = dotenv.dotenv_values('.env')
token = config['token']
request_url = config['request_url']
make_requests = (config['make_requests'] == 'True')
save_info = (config['save_info'] == 'True')
matches_saving_file = config['matches_saving_file']
teams_saving_file = config['teams_saving_file']
players_saving_file = config['players_saving_file']

def make_request_teams():
    r"""Получает данные о командах с сервера при запуске.
    
    Если сервер не отвечает или make_requests=False, то возвращает None"""
    if not make_requests:
        return None
    response = requests.get(request_url + "/teams", headers={"Authorization": token})
    if not response.ok:
        return None
    teams = response.json()
    teams = pd.DataFrame(teams)
    return teams

def make_request_players(players_id):
    r"""Получает данные о игроках с сервера при запуске.
    
    Если сервер не отвечает или make_requests=False, то возвращает None"""
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
    r"""Получает данные о матчах с сервера при запуске.
    
    Если сервер не отвечает или make_requests=False, то возвращает None"""
    if not make_requests:
        return None
    response = requests.get(request_url + "/matches", headers={"Authorization": token})
    if not response.ok:
        return None
    matches = response.json()
    matches = pd.DataFrame(matches)
    return matches

def init(more_info=False):
    r"""Возвращает переменные teams, matches, players.
    
    Если сервер не работает или make_requests=False, то берёт сохранённые данные. Если save_info=True, то сохраняет данные

    Если more_info=True, то также возвращает получены ли переменные от сервера. (True - данные получены от сервера)
    """
    teams = make_request_teams()
    teams_from_server = True
    if teams is None:
        teams_from_server = False
        teams = pd.read_csv(teams_saving_file)
    elif save_info:
        teams.to_csv(teams_saving_file)

    matches = make_request_matches()
    matches_from_server = True
    if matches is None:
        matches_from_server = False
        matches = pd.read_csv(matches_saving_file)
    elif save_info:
        matches.to_csv(matches_saving_file)

    players_and_teams_id = pd.DataFrame({'id': [], 'team_id': []})
    for i in range(len(teams)):
        lst = teams['players'][i]
        team_id = teams['id'][i]
        for x in lst:
            players_and_teams_id.loc[len(players_and_teams_id)] = {'id': x, 'team_id': team_id}
    players = make_request_players(players_and_teams_id['id'])
    players_from_server = True
    if players is None:
        players_from_server = False
        players = pd.read_csv(players_saving_file)
    else:
        players = pd.merge(players, players_and_teams_id, on='id')
        if save_info:
            players.to_csv(players_saving_file)
    players['name'] = players['name'].apply(lambda x: '' if pd.isna(x) else x)
    players['surname'] = players['surname'].apply(lambda x: '' if pd.isna(x) else x)

    if more_info:
        return teams, matches, players, teams_from_server, matches_from_server, players_from_server
    return teams, matches, players

teams, matches, players, teams_from_server, matches_from_server, players_from_server = init(more_info=True)

def stats(team_name):
    """Возвращает статистику по команде (количество побед, поражений, разница между забитыми и пропущенными голами)"""
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

def get_team(player_id):
    """Возвращает id команды по id игрока. Если такого игрока нет, то возвращает None"""
    if len(players[players['id'] == player_id]) != 1:
        return None
    return list(players[players['id'] == player_id]['team_id'])[0]

def versus(player1_id, player2_id):
    team1_id = get_team(player1_id)
    team2_id = get_team(player2_id)
    if team1_id is None or team2_id is None or team1_id == team2_id:
        return 0
    return len(matches[((matches['team1'] == team1_id) & (matches['team2'] == team2_id)) |\
                       ((matches['team1'] == team2_id) & (matches['team2'] == team1_id))])

def get_request():
    """Получает запрос от пользователя"""
    request = input().split(maxsplit=1)
    if request[0] == "exit":
        return "exit", []
    elif request[0] == "info":
        return "info", []
    elif request[0] == "stats?":
        return "stats", [request[1][1:-1]]
    elif request[0] == "versus?":
        request[1] = request[1].split()
        return "versus", [int(request[1][0]), int(request[1][1])]
    else:
        return "?", []
    
def get_list_of_players():
    """Возвращает список игроков в лексикографическом порядке"""
    lst = []
    for i in range(len(players)):
        lst.append(str(players['name'][i]) + ' ' + str(players['surname'][i]))
    lst.sort()
    return lst

def process_request(request_type, params):
    """Обрабатывает запрос от пользователя"""
    if request_type == "exit":
        return False
    
    if request_type == "stats":
        wins, losings, goals = stats(params[0])
        print(wins, losings, goals)
    elif request_type == "versus":
        print(versus(params[0], params[1]))
    else:
        print("Unknow request")
    return True

if __name__ == "__main__":
    all_players = get_list_of_players()
    for x in all_players:
        print(x)

    while True:
        request_type, params = get_request()
        if not process_request(request_type, params):
            break
        

