import main
"""
Для тестирования нужно изменить эти параметры в .env:

make_requests="False"
save_info="False"
matches_saving_file="matches_test.csv"
teams_saving_file="teams_test.csv"
players_saving_file="players_test.csv"

"""

print(main.matches)
print(main.teams)
print(main.players)

all_players = main.get_list_of_players()
print("Players:")
print(all_players)
assert all_players == [' ', ' Hello World!', ' surname2', '21 21', 'Big ',\
                       'No Нет', 'P P', 'misha ', 'name sur-name', 'name1 surname1',
                       'nameeeee surnam', 'noname noname hi', 'имя Фамилия', 'нет идей no ideas']

"""Тестирование функции stats"""
t1_stats = main.stats("Team1")
print("Team 1 stats:", t1_stats)
assert t1_stats == (2, 1, 7)

t2_stats = main.stats("Команда 2")
print("Team 2 stats:", t2_stats)
assert t2_stats == (2, 1, 2)

t3_stats = main.stats("Team 3")
print("Team 3 stats:", t3_stats)
assert t3_stats == (0, 2, -9)

t4_stats = main.stats("Team4")
print("Team 4 stats:", t4_stats)
assert t4_stats == (1, 0, 10)

t5_stats = main.stats("Team5")
print("Team 5 stats:", t5_stats)
assert t5_stats == (0, 1, -10)

t0_stats = main.stats("Unknow team")
print("Unkonow team stats:", t0_stats)
assert t0_stats == (0, 0, 0)

"""Тестирование функции versus"""
versus_1_2 = main.versus(1, 2)
print("1 vs 2:", versus_1_2)
assert versus_1_2 == 0

versus_4_115 = main.versus(4, 115)
print("4 vs 115:", versus_4_115)
assert versus_4_115 == 1

versus_10_9 = main.versus(10, 9)
print("10 vs 9:", versus_10_9)
assert versus_10_9 == 0

versus_14_2 = main.versus(14, 2)
print("14 vs 2:", versus_14_2)
assert versus_14_2 == 3

versus_0_2 = main.versus(0, 2)
print("0 vs 2:", versus_0_2)
assert versus_0_2 == 0

print("OK")