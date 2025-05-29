# Вступительная работа в ЛКШ 2025 на параллель P

## Как запустить
1. Скопировать файл .env_example в .env
2. Изменить в .env переменную token на нужный токен
3. Установить модули `pip install -r .\requirements.txt`
   
   ![image](https://github.com/user-attachments/assets/fc63acbe-fdc3-4402-9ffd-824a42dbe4ff)
4. Запустить main.py `python main.py`
   
   ![image](https://github.com/user-attachments/assets/3c89ba16-21de-4306-be9b-1d451339bb89)


## Как использовать
* versus? player_id_1 player_id_2 - количество игр между командами этих игроков

  ![image](https://github.com/user-attachments/assets/e7c1ff7e-cb98-4872-bd1c-6db9101c2616)
* stats? team_name - количество побед команды, количество поражений и разница между забитыми и пропущенными голами

  ![image](https://github.com/user-attachments/assets/51522ab0-e32e-4af6-901b-25cb2f5056e9)
* exit - завершить выполнение программы

  ![image](https://github.com/user-attachments/assets/bb177179-56a4-4526-a72c-7d77e130ffc7)

## Тестирование
* Изменить некоторые параметры в .env (об этом написано в test.py)
* Запустить файл test.py
