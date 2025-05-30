import requests
import pandas as pd
import datetime
import dotenv

zero_time = '2000-01-01'
def now():
    """Возвращает время в str"""
    return str(pd.to_datetime(f"{datetime.datetime.now()}"))

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
        r"""Получает данные о игроках с id, содержащимися в списке players_id, с сервера при запуске.
        
        Если сервер не отвечает или make_requests=False, то возвращает None"""
        if not self.make_requests:
            return None
        players = pd.DataFrame()
        for id in players_id:
            response = requests.get(self.__request_url + "/players/" + str(id), headers={"Authorization": self.__token})
            if not response.ok:
                self.last_failed_request = self.__request_url + "/players" + str(id)
                self.response_to_last_failed_request = response
                return None
            player = response.json()
            players = pd.concat([players, pd.DataFrame([player])], ignore_index=True)
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

    def __make_request_goals(self, matches_id):
        r"""Получает подробные данные данные о матчах с id, содержащихся в matches_id, с сервера при запуске.
        
        Если сервер не отвечает или make_requests=False, то возвращает None"""
        if not self.make_requests:
            return None
        goals = pd.DataFrame()
        for match_id in matches_id:
            response = requests.get(self.__request_url + "/goals", headers={"Authorization": self.__token}, params={'match_id': match_id})
            if not response.ok:
                self.last_failed_request = self.__request_url + "/goals" + "?match_id=" + str(match_id)
                self.response_to_last_failed_request = response
                return None
            goals_in_match = response.json()
            goals_in_match = pd.DataFrame(goals_in_match)
            goals = pd.concat([goals, goals_in_match], ignore_index=True)
        return goals

    def __update_players_saving_time_file(self):
        r"""Проверяет все ли id игроков добавлены в time_saving, и если нет, то обновляет time_saving"""
        change = False
        for team_id, list_id in self.__teams['id'].values, self.__teams['players'].values:
            for id in list_id:
                if not(int(id) in self.__time_saving[self.__time_saving['type'] == 'player']['id'].values):
                    self.__players_time_saving = pd.concat([self.__players_time_saving, pd.DataFrame({'team_id': team_id, 'id': [id], 'time': [zero_time]})], ignore_index=True)
                    change = True

        if change:
            self.__players_time_saving.to_csv(self.__players_saving_time_file, index=False)

    def __update_saving_time_file(self):
        r"""Проверяет все ли id игроков и матчей добавлены в time_saving, и если нет, то обновляет time_saving"""
        change = False
        for list_id in self.__teams['players']:
            for id in list_id:
                if not(int(id) in self.__time_saving[self.__time_saving['type'] == 'player']['id'].values):
                    self.__time_saving = pd.concat([self.__time_saving, pd.DataFrame({'type': ['player'], 'id': [id], 'time': [zero_time]})], ignore_index=True)
                    change = True
        for id in self.__matches['id']:
            if not(int(id) in self.__time_saving[self.__time_saving['type'] == 'match']['id'].values):
                self.__time_saving = pd.concat([self.__time_saving, pd.DataFrame({'type': ['match'], 'id': [id], 'time': [zero_time]})], ignore_index=True)
                change = True

        if change:
            self.__time_saving.to_csv(self.saving_time_file, index=False)

    def update_data(self, count=-1, bad_time=pd.Timedelta(days=1.0)):
        r"""Обновляет данные путём запросов на сервер
        
        Ничего не делает, если make_requests=False

        Обновляет данные о командах и матчах, если последний раз они обновлялись bad_time времени назад или раньше

        Обновляет данные о count игроках (берутся те, что дольше всего не обновлялись). Если count=-1, то обновляет данные обо всех

        Обновляет данные о голах в count матчах (берутся те, что дольше всего не обновлялись). Если count=-1, то обновляет данные обо всех
        
        Сохраняет новый time_saving
        """
        if not self.make_requests:
            return
        if (pd.to_datetime(now()) - pd.to_datetime(self.__last_teams_update)) > bad_time:
            self.__teams = self.__make_request_teams()
            if not (self.__teams is None):
                self.__teams.to_csv(self.teams_saving_file, index=False)
                self.__last_teams_update = now()
        
        if (pd.to_datetime(now()) - pd.to_datetime(self.__last_matches_update)) > bad_time:
            self.__matches = self.__make_request_matches()
            if not (self.__matches is None):
                self.__matches.to_csv(self.matches_saving_file, index=False)
                self.__last_matches_update = now()
        self.__update_saving_time_file()

        count_minus_one = False
        if count == -1:
            count_minus_one = True

        self.__time_saving = self.__time_saving.sort_values('time')

        players_id = []

        if count_minus_one:
            count = len(self.__time_saving[self.__time_saving['type'] == 'player']['id'])
        players_id = list(self.__time_saving[self.__time_saving['type'] == 'player']['id'][:count])
        players = self.__make_request_players(players_id)
        if players is None:
            return False
        self.__players = pd.concat([self.__players[~self.__players['id'].isin(players_id)], players], ignore_index=True)
        self.__time_saving = pd.concat([self.__time_saving[(self.__time_saving['type'] == 'match') | (~self.__time_saving['id'].isin(players_id))],\
                                pd.DataFrame({'id': players_id, 'type': ['player' for _ in range(count)], 'time': [now() for _ in range(count)]})], ignore_index=True)
        self.__players.to_csv(self.players_saving_file, index=False)
        
        matches_id = []
        if count_minus_one:
            count = len(self.__time_saving[self.__time_saving['type'] == 'match']['id'])
        matches_id = list(self.__time_saving[self.__time_saving['type'] == 'match']['id'][:count])
        goals = self.__make_request_goals(matches_id)
        if goals is None:
            return False
        self.__goals = pd.concat([self.__goals[~self.__goals['match'].isin(matches_id)], goals], ignore_index=True)
        self.__time_saving = pd.concat([self.__time_saving[(self.__time_saving['type'] == 'player') | (~self.__time_saving['id'].isin(matches_id))],\
                                pd.DataFrame({'id': matches_id, 'type': ['match' for _ in range(count)], 'time': [now() for _ in range(count)]})], ignore_index=True)
        self.__goals.to_csv(self.goals_saving_file, index=False)

        self.__time_saving.to_csv(self.saving_time_file, index=False)
        return True


    def __init__(self, config, init_info=False):
        r"""Инициализирует переменные __teams, __matches, __players.
        
        Если сервер не работает или make_requests=False, то берёт сохранённые данные. Если save_info=True, то сохраняет данные
        
        Если init_info=True, то выводит в консоль, когда завершается загрузка данных о командах, матчах, игроках и голах
        
        В config должны быть такие ключи:
        
        1. token - токен
        2. request_url - адрес сайта, с которого берём данные
        3. make_requests - True, если нужно брать данные с сайта, False - иначе
        4. matches_saving_file - путь, по которому сохраняем данные о матчах
        5. teams_saving_file - путь, по которому сохраняем данные о командах
        6. players_saving_file - путь, по которому сохраняем данные о игроках
        7. goals_saving_file - путь, по которому сохраняем данные о голах
        8. saving_time_file - путь, по которому сохраняем последнее время обновления данных
        """

        self.__token = config['token']
        self.__request_url = config['request_url']
        self.make_requests = (config['make_requests'] == 'True')
        self.matches_saving_file = config['matches_saving_file']
        self.teams_saving_file = config['teams_saving_file']
        self.players_saving_file = config['players_saving_file']
        self.goals_saving_file = config['goals_saving_file']
        self.__players_saving_time_file = config['players_saving_time_file']
        self.last_failed_request = None
        self.response_to_last_failed_request = None
        
        self.__last_teams_update = zero_time
        self.__last_matches_update = zero_time
        self.__time_saving = pd.read_csv(self.saving_time_file)

        self.__teams = pd.read_csv(self.teams_saving_file)
        self.__matches = pd.read_csv(self.matches_saving_file)
        self.__players = pd.read_csv(self.players_saving_file)
        self.__goals = pd.read_csv(self.goals_saving_file)

        self.update_data(count=0)

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
        """Возвращает количество игр между командами игроков player1_id и player2_id"""
        team1_id = self.get_team(player1_id)
        team2_id = self.get_team(player2_id)
        if team1_id is None or team2_id is None or team1_id == team2_id:
            return 0
        return len(self.__matches[((self.__matches['team1'] == team1_id) & (self.__matches['team2'] == team2_id)) |\
                        ((self.__matches['team1'] == team2_id) & (self.__matches['team2'] == team1_id))])
    
    def goals(self, player_id):
        """Возвращает все голы игрока (id матча и время)"""
        return self.__goals[self.__goals['player'] == player_id].drop(columns=['player', 'goal_id']).to_dict('records')


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
    elif request[0] == "upd":
        return "upd", [int(request[1])]
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
    
    if request_type == "upd":
        if sdb.update_data(count=params[0]):
            print("OK")
        else:
            print("Error")
    elif request_type == "lfr":
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