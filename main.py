import requests
import pandas as pd
import dotenv

class Sport_Database():
    def __make_request_teams(self):
        r"""Получает данные о командах с сервера при запуске.
        
        Если сервер не отвечает или make_requests=False, то возвращает None"""
        if not self.make_requests:
            return None
        response = requests.get(self.__request_url + "/teams", headers={"Authorization": self.__token})
        if not response.ok:
            self.last_failed_request = self.__request_url + "/teams"
            self.response_to_last_failed_request = response
            return None
        teams = response.json()
        teams = pd.DataFrame(teams)
        return teams

    def __make_request_players(self, players_id):
        r"""Получает данные о игроках с сервера при запуске.
        
        Если сервер не отвечает или make_requests=False, то возвращает None"""
        if not self.make_requests:
            return None
        players = pd.DataFrame({"id": [], "name": [], "surname": [], "number": []})
        for id in players_id:
            response = requests.get(self.__request_url + "/players/" + str(id), headers={"Authorization": self.__token})
            if not response.ok:
                self.last_failed_request = self.__request_url + "/players" + str(id)
                self.response_to_last_failed_request = response
                return None
            player = response.json()
            players.loc[len(players)] = player
        return players
            
    def __make_request_matches(self):
        r"""Получает данные о матчах с сервера при запуске.
        
        Если сервер не отвечает или make_requests=False, то возвращает None"""
        if not self.make_requests:
            return None
        response = requests.get(self.__request_url + "/matches", headers={"Authorization": self.__token})
        if not response.ok:
            self.last_failed_request = self.__request_url + "/matches"
            self.response_to_last_failed_request = response
            return None
        matches = response.json()
        matches = pd.DataFrame(matches)
        return matches

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

        self.__token = config['token']
        self.__request_url = config['request_url']
        self.make_requests = (config['make_requests'] == 'True')
        self.save_info = (config['save_info'] == 'True')
        self.matches_saving_file = config['matches_saving_file']
        self.teams_saving_file = config['teams_saving_file']
        self.players_saving_file = config['players_saving_file']
        self.last_failed_request = None
        self.response_to_last_failed_request = None

        self.__teams = self.__make_request_teams()
        if self.__teams is None:
            self.__teams = pd.read_csv(self.teams_saving_file)
        elif self.save_info:
            self.__teams.to_csv(self.teams_saving_file)

        self.__matches = self.__make_request_matches()
        if self.__matches is None:
            self.__matches = pd.read_csv(self.matches_saving_file)
        elif self.save_info:
            self.__matches.to_csv(self.matches_saving_file)

        players_and_teams_id = pd.DataFrame({'id': [], 'team_id': []})
        for i in range(len(self.__teams)):
            lst = self.__teams['players'][i]
            team_id = self.__teams['id'][i]
            for x in lst:
                players_and_teams_id.loc[len(players_and_teams_id)] = {'id': x, 'team_id': team_id}
        self.__players = self.__make_request_players(players_and_teams_id['id'])
        if self.__players is None:
            self.__players = pd.read_csv(self.players_saving_file)
        else:
            self.__players = pd.merge(self.__players, players_and_teams_id, on='id')
            if self.save_info:
                self.__players.to_csv(self.players_saving_file)
        self.__players['name'] = self.__players['name'].apply(lambda x: '' if pd.isna(x) else x)
        self.__players['surname'] = self.__players['surname'].apply(lambda x: '' if pd.isna(x) else x)

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

    def get_team(self, player_id):
        """Возвращает id команды по id игрока. Если такого игрока нет, то возвращает None"""
        if len(self.__players[self.__players['id'] == player_id]) != 1:
            return None
        return list(self.__players[self.__players['id'] == player_id]['team_id'])[0]

    def versus(self, player1_id, player2_id):
        team1_id = self.get_team(player1_id)
        team2_id = self.get_team(player2_id)
        if team1_id is None or team2_id is None or team1_id == team2_id:
            return 0
        return len(self.__matches[((self.__matches['team1'] == team1_id) & (self.__matches['team2'] == team2_id)) |\
                        ((self.__matches['team1'] == team2_id) & (self.__matches['team2'] == team1_id))])
        
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