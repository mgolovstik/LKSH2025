# Вступительная работа в ЛКШ 2025 на параллель P

## Как запустить консольную версию
1. Скопировать файл .env_example в .env
2. Изменить в .env переменную token на нужный токен
3. Установить модули `pip install -r .\requirements.txt`
   
   ![image](https://github.com/user-attachments/assets/fc63acbe-fdc3-4402-9ffd-824a42dbe4ff)
4. Запустить main.py `python main.py`

![image](https://github.com/user-attachments/assets/3c89ba16-21de-4306-be9b-1d451339bb89)
5. Если make_requests=True, то запуск может занимать примерно 5 минут

## Как использовать консольную версию
* versus? player_id_1 player_id_2 - количество игр между командами этих игроков

  ![image](https://github.com/user-attachments/assets/e7c1ff7e-cb98-4872-bd1c-6db9101c2616)
* stats? team_name - количество побед команды, количество поражений и разница между забитыми и пропущенными голами

  ![image](https://github.com/user-attachments/assets/51522ab0-e32e-4af6-901b-25cb2f5056e9)
* exit - завершить выполнение программы

  ![image](https://github.com/user-attachments/assets/bb177179-56a4-4526-a72c-7d77e130ffc7)
* lfr - последний неудачный запрос на сервер lksh и ответ на него 

## Тестирование консольной версии
1. Установить модули `pip install -r .\requirements.txt`
2. Запустить test.py `python test.py`

## Как запустить сервер
1. Скопировать файл .env_example в .env
2. Изменить в .env переменную token на нужный токен
3. Установить модули `pip install -r .\requirements.txt`
4. Запустить server.py `python server.py`
5. Если make_requests=True, то запуск может занимать примерно 5 минут

## Как использовать сервер
* Сервер запускается на порту 5000, изменить порт можно в .env
* /stats?team_name=<team_name> - количество побед команды c именем <team_name>, количество поражений и разница между забитыми и пропущенными голами
* /versus?player1_id=<player1_id>&player2_id=<player2_id> - количество игр между командами игроков с id <player1_id> и <player2_id>
* /goals?player_id=<player_id> - список голов игрока с id <player_id> (id матча и время)
* /lfr - последний неудачный запрос на сервер lksh и ответ на него
* / - главная страница

  ![image](https://github.com/user-attachments/assets/3de339f7-7c0b-4d6a-8169-a39f1908180d)
* /front/stats - HTML-интерфейс для статистики команд

  ![image](https://github.com/user-attachments/assets/f27ec252-ec22-4bd7-911a-fb088da8c893)
* /front/versus - HTML-интерфейс для сравнения игроков

  ![image](https://github.com/user-attachments/assets/62effbb1-ae92-4648-95db-188a97bfb3ac)

## Дополнительные параметры в .env
* make_requests - Если False, то не будут отправляться запросы на сервер lksh, будут использоваться сохранённые данные
* save_info - Если True, то будет локально сохранять полученные при запуске данные
* port - Порт, с которого будет запускаться сервер
* request_url - Адрес сервера, с которого берутся данные

## Docker

Эту часть добавил [igel2000](https://github.com/igel2000). Всё остальное я делал сам.

### Самостоятельная сборка образа

Создать образ:
```
docker build -t lksh .
```

Запустить контейнер:
```
docker run -d --rm -p 5000:5000 -v $(pwd)/.env:/app/.env lksh
```

### Использование готового образа

Загрузить образ:
```
docker pull igel2000/lksh
```

Запустить контейнер:
```
docker run -d --rm -p 5000:5000 -v $(pwd)/.env:/app/.env igel2000/lksh
```
