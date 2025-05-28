from flask import Flask
from flask import request
import main
import dotenv

config = dotenv.dotenv_values('.env')
app = Flask(__name__)
sdb = main.Sport_Database(config=config)

@app.route('/lfr')
def last_failed_request_info():
   lfr, rlfr = sdb.get_last_failed_request_info()
   return {"Last failed request": lfr, "Response to last failed request": rlfr}

@app.route('/stats')
def stats():
   team_name = request.args.get('team_name', '')
   wins, loosings, goals = sdb.stats(team_name=team_name)
   return {"Wins": wins, "Loosings": loosings, "Goals": goals}

@app.route('/versus')
def versus():
   player1_id = int(request.args.get('player1_id', '-1'))
   player2_id = int(request.args.get('player2_id', '-1'))
   count = sdb.versus(player1_id, player2_id)
   return {"Matches": count}

if __name__ == '__main__':
   app.run(port=config['port'])