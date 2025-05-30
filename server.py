from flask import Flask, render_template
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

@app.route('/front/stats')
def front_stats():
   team_name = request.args.get('team_name', '')
   wins, loosings, goals = sdb.stats(team_name)
   return render_template('stats.html', name=team_name, wins=wins, loosings=loosings, goals=goals)

@app.route('/front/versus')
def front_versus():
   player1_id = request.args.get('player1_id', '')
   player2_id = request.args.get('player2_id', '')
   count = sdb.versus(player1_id, player2_id)
   return render_template('versus.html', player1_id=player1_id, player2_id=player2_id, count=count)

@app.route('/stats')
def stats():
   team_name = request.args.get('team_name', '')
   wins, loosings, goals = sdb.stats(team_name=team_name)
   return {"Wins": wins, "Loosings": loosings, "Goals": goals}

@app.route('/versus')
def versus():
   player1_id = request.args.get('player1_id', '-1')
   player2_id = request.args.get('player2_id', '-1')
   count = sdb.versus(player1_id, player2_id)
   return {"Matches": count}

@app.route('/goals')
def goals():
   player_id = request.args.get('player_id', '0')
   return sdb.goals(player_id)

@app.route('/')
def main_page():
   return render_template('main_page.html')

if __name__ == '__main__':
   app.run(port=config['port'], host='0.0.0.0') #, host='0.0.0.0'