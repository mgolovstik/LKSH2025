import main
import dotenv

config = {
        'token': None,\
        'request_url': None,\
        'make_requests': "False",\
        'save_info': "False",\
        'matches_saving_file': "test_data/matches_test.csv",\
        'teams_saving_file': "test_data/teams_test.csv",\
        'players_saving_file': "test_data/players_test.csv",\
        'goals_saving_file': "test_data/goals_test.csv"
        }
sdb = main.Sport_Database(config=config)

teams, matches, players = sdb.get_data()
print(matches)
print(teams)
print(players)

all_players = sdb.get_list_of_players()
print("Players:")
print(all_players)
assert all_players == [' ', ' Hello World!', ' surname2', '21 21', 'Big ',\
                       'No Нет', 'P P', 'misha ', 'name sur-name', 'name1 surname1',
                       'nameeeee surnam', 'noname noname hi', 'имя Фамилия', 'нет идей no ideas']

"""Тестирование функции stats"""
t1_stats = sdb.stats("Team1")
print("Team 1 stats:", t1_stats)
assert t1_stats == (2, 1, 7)

t2_stats = sdb.stats("Команда 2")
print("Team 2 stats:", t2_stats)
assert t2_stats == (2, 1, 2)

t3_stats = sdb.stats("Team 3")
print("Team 3 stats:", t3_stats)
assert t3_stats == (0, 2, -9)

t4_stats = sdb.stats("Team4")
print("Team 4 stats:", t4_stats)
assert t4_stats == (1, 0, 10)

t5_stats = sdb.stats("Team5")
print("Team 5 stats:", t5_stats)
assert t5_stats == (0, 1, -10)

t0_stats = sdb.stats("Unknow team")
print("Unkonow team stats:", t0_stats)
assert t0_stats == (0, 0, 0)

"""Тестирование функции versus"""
versus_1_2 = sdb.versus(1, 2)
print("1 vs 2:", versus_1_2)
assert versus_1_2 == 0

versus_4_115 = sdb.versus(4, 115)
print("4 vs 115:", versus_4_115)
assert versus_4_115 == 1

versus_10_9 = sdb.versus(10, 9)
print("10 vs 9:", versus_10_9)
assert versus_10_9 == 0

versus_14_2 = sdb.versus(14, 2)
print("14 vs 2:", versus_14_2)
assert versus_14_2 == 3

versus_0_2 = sdb.versus(0, 2)
print("0 vs 2:", versus_0_2)
assert versus_0_2 == 0

"""Тестирование функции goals"""
goals_1 = sdb.goals(1)
print("goals? 1:", goals_1)
assert goals_1 == [{'match': 0, 'time': 41}, {'match': 2, 'time': 31}] or\
        goals_1 == [{'match': 2, 'time': 31}, {'match': 0, 'time': 41}]

goals_2 = sdb.goals(2)
print("goals? 2:", goals_2)
assert goals_2 == [{'match': 2, 'time': 30}]

goals_9 = sdb.goals(9)
print("goals? 9:", goals_9)
assert goals_9 == [{'match': 4, 'time': 100}]

goals_10 = sdb.goals(10)
print("goals? 10:", goals_10)
assert goals_10 == [{'match': 2, 'time': 10}]

goals_unknow = sdb.goals(404)
print("goals? unknow:", goals_unknow)
assert goals_unknow == []

print("OK")