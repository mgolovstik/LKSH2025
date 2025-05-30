import requests
import pandas as pd
import dotenv
import time

def to_id(id):
    """Если id целоче число (строка или int), то возвращает int с его значением, если нет, то -1"""
    if isinstance(id, str):
        if id.isdigit():
            id = int(id)
    if not isinstance(id, int):
        id = -1
    return id

class Sport_Database():
    def __make_request_teams(self):
        r"""Получает данные о командах с сервера при запуске.
        
        Если сервер не отвечает или make_requests=False, то возвращает None"""
        if not self.make_requests:
            return None
        response = requests.get(self.request_url + "/teams", headers={"Authorization": self.token})
        if not response.ok:
            self.last_failed_request = self.request_url + "/teams"
            self.response_to_last_failed_request = response
            return None
        teams = response.json()
        teams = pd.DataFrame(teams)
        return teams
            
    def __make_request_matches(self):
        r"""Получает данные о матчах с сервера при запуске.
        
        Если сервер не отвечает или make_requests=False, то возвращает None"""
        if not self.make_requests:
            return None
        response = requests.get(self.request_url + "/matches", headers={"Authorization": self.token})
        if not response.ok:
            self.last_failed_request = self.request_url + "/matches"
            self.response_to_last_failed_request = response
            return None
        matches = response.json()
        matches = pd.DataFrame(matches)
        return matches

    def __make_request_players(self, players_id):
        r"""Получает данные о игроках с сервера при запуске.
        
        Если сервер не отвечает или make_requests=False, то возвращает None"""
        if not self.make_requests:
            return None
        players = []
        for id in players_id:
            response = None
            while response is None:
                response = requests.get(self.request_url + "/players/" + str(id), headers={"Authorization": self.token})
                if response.status_code == 429:
                    time.sleep(1.0)
                    response = None
            if not response.ok:
                self.last_failed_request = self.request_url + "/players/" + str(id)
                self.response_to_last_failed_request = response
                return None
            player = response.json()
            players.append(player)
        players = pd.DataFrame(players)
        return players

    def __make_request_goals(self, matches_id):
        r"""Получает данные о голах с сервера при запуске.
        
        Если сервер не отвечает или make_requests=False, то возвращает None"""
        if not self.make_requests:
            return None
        goals = []
        for id in matches_id:
            response = None
            while response is None:
                response = requests.get(self.request_url + "/goals", headers={"Authorization": self.token}, params={'match_id': id})
                if response.status_code == 429:
                    time.sleep(1.0)
                    response = None
            if not response.ok:
                self.last_failed_request = self.request_url + "/goals?match_id=" + str(id)
                self.response_to_last_failed_request = response
                return None
            goals += response.json()
        goals = pd.DataFrame(goals)
        goals = goals.rename(columns={'minute': 'time'})
        return goals

    def __init__(self, config):
        r"""Инициализирует переменные __teams, __matches, __players.
        
        Если сервер не работает или make_requests=False, то берёт сохранённые данные. Если save_info=True, то сохраняет данные
        
        В config должны быть такие ключи:
        
        1. token - токен
        2. request_url - адрес сайта, с которого берём данные
        3. make_requests - True, если нужно брать данные с сайта, False - иначе
        4. save_info - True, если нужно локально сохранять данные, False - иначе
        5. matches_saving_file - путь, по которому сохраняем данные о матчах
        6. teams_saving_file - путь, по которому сохраняем данные о командах
        7. players_saving_file - путь, по которому сохраняем данные о игроках
        """

        self.token = config['token']
        self.request_url = config['request_url']
        self.make_requests = (config['make_requests'] == 'True')
        self.save_info = (config['save_info'] == 'True')
        self.matches_saving_file = config['matches_saving_file']
        self.teams_saving_file = config['teams_saving_file']
        self.players_saving_file = config['players_saving_file']
        self.goals_saving_file = config['goals_saving_file']
        self.last_failed_request = None
        self.response_to_last_failed_request = None

        self.__teams = self.__make_request_teams()
        if self.__teams is None:
            self.__teams = pd.read_csv(self.teams_saving_file)
        elif self.save_info:
            self.__teams.to_csv(self.teams_saving_file, index=False)

        self.__matches = self.__make_request_matches()
        if self.__matches is None:
            self.__matches = pd.read_csv(self.matches_saving_file)
        elif self.save_info:
            self.__matches.to_csv(self.matches_saving_file, index=False)

        players_and_teams_id = []
        for i in range(len(self.__teams)):
            lst = self.__teams['players'][i]
            team_id = self.__teams['id'][i]
            for x in lst:
                players_and_teams_id.append({'id': x, 'team_id': team_id})
        players_and_teams_id = pd.DataFrame(players_and_teams_id)
        self.__players = self.__make_request_players(players_and_teams_id['id'])
        if self.__players is None:
            self.__players = pd.read_csv(self.players_saving_file)
        else:
            self.__players = pd.merge(self.__players, players_and_teams_id, on='id')
            if self.save_info:
                self.__players.to_csv(self.players_saving_file, index=False)
        self.__players['name'] = self.__players['name'].apply(lambda x: '' if pd.isna(x) else x)
        self.__players['surname'] = self.__players['surname'].apply(lambda x: '' if pd.isna(x) else x)

        self.__goals = self.__make_request_goals(matches_id=list(self.__matches['id']))
        if self.__goals is None:
            self.__goals = pd.read_csv(self.goals_saving_file)
        elif self.save_info:
            self.__goals.to_csv(self.goals_saving_file, index=False)

    def stats(self, team_name):
        """Возвращает статистику по команде (количество побед, поражений, разница между забитыми и пропущенными голами)"""
        if len(self.__teams[self.__teams['name'] == team_name]) == 0:
            return 0, 0, 0
        team_id = list(self.__teams[self.__teams['name'] == team_name]['id'])[0]
        wins = len(self.__matches[(self.__matches['team1'] == team_id) & (self.__matches['team1_score'] > self.__matches['team2_score'])])\
            + len(self.__matches[(self.__matches['team2'] == team_id) & (self.__matches['team1_score'] < self.__matches['team2_score'])])
        losings = len(self.__matches[(self.__matches['team1'] == team_id) & (self.__matches['team1_score'] < self.__matches['team2_score'])])\
            + len(self.__matches[(self.__matches['team2'] == team_id) & (self.__matches['team1_score'] > self.__matches['team2_score'])])
        goals = self.__matches[self.__matches['team1'] == team_id]['team1_score'].sum() + self.__matches[self.__matches['team2'] == team_id]['team2_score'].sum()\
            - self.__matches[self.__matches['team2'] == team_id]['team1_score'].sum() - self.__matches[self.__matches['team1'] == team_id]['team2_score'].sum()
        return wins, losings, int(goals)

    def __get_team(self, player_id):
        """Возвращает id команды по id игрока. Если такого игрока нет, то возвращает None"""
        if len(self.__players[self.__players['id'] == player_id]) != 1:
            return None
        return list(self.__players[self.__players['id'] == player_id]['team_id'])[0]

    def versus(self, player1_id, player2_id):
        r"""Возвращает количество матчей, в которых соревновались команды двух игроков
        
        Если id задан строкой, то преобразует его
        """
        player1_id = to_id(player1_id)
        player2_id = to_id(player2_id)
        team1_id = self.__get_team(player1_id)
        team2_id = self.__get_team(player2_id)
        if team1_id is None or team2_id is None or team1_id == team2_id:
            return 0
        return len(self.__matches[((self.__matches['team1'] == team1_id) & (self.__matches['team2'] == team2_id)) |\
                        ((self.__matches['team1'] == team2_id) & (self.__matches['team2'] == team1_id))])
    
    def goals(self, player_id):
        """Возвращает список голов игрока (матч и time)"""
        player_id = to_id(player_id)
        if self.__get_team(player_id) is None:
            return []
        return self.__goals[self.__goals['player'] == player_id].drop(columns=['id', 'player']).to_dict(orient='records')

    def get_list_of_players(self):
        """Возвращает список игроков в лексикографическом порядке"""
        lst = []
        for i in range(len(self.__players)):
            lst.append(str(self.__players['name'][i]) + ' ' + str(self.__players['surname'][i]))
        lst.sort()
        return lst
    
    def get_data(self):
        """Возвращает переменные __teams, __matches, __players"""
        return self.__teams, self.__matches, self.__players
    
    def get_last_failed_request_info(self):
        """Возвращает последней неудачный запрос и ответ на него"""
        return self.last_failed_request, (None if self.response_to_last_failed_request is None else self.response_to_last_failed_request.text)
            

def get_request():
    """Получает запрос от пользователя"""
    request = input().split(maxsplit=1)
    if request[0] == "exit":
        return "exit", []
    elif request[0] == "lfr":
        return "lfr", []
    elif request[0] == "stats?":
        return "stats", [request[1][1:-1]]
    elif request[0] == "versus?":
        request[1] = request[1].split()
        return "versus", [int(request[1][0]), int(request[1][1])]
    elif request[0] == "goals?":
        return "goals", [int(request[1])]
    else:
        return "?", []

def process_request(request_type, params, sdb:Sport_Database):
    """Обрабатывает запрос от пользователя"""
    if request_type == "exit":
        return False
    
    if request_type == "lfr":
        lfr, rlfr = sdb.get_last_failed_request_info()
        print("Last failed request:", lfr)
        print("Response to last failed request:", rlfr)
    elif request_type == "goals":
        lst = sdb.goals(params[0])
        print(lst)
    elif request_type == "stats":
        wins, losings, goals = sdb.stats(params[0])
        print(wins, losings, goals)
    elif request_type == "versus":
        print(sdb.versus(params[0], params[1]))
    else:
        print("Unknow request")
    return True

if __name__ == "__main__":
    config = dotenv.dotenv_values('.env')
    sdb = Sport_Database(config=config)
    all_players = sdb.get_list_of_players()
    for x in all_players:
        print(x)

    while True:
        request_type, params = get_request()
        if not process_request(request_type, params, sdb):
            break