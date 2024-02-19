from flask import Flask, jsonify,render_template
from utils.find_matches import find_matches_nba, find_matches_nhl
import utils.odds_and_lines_utils.get_betonline_odds as get_betonline_odds
from utils.odds_and_lines_utils.nba.scrape_nba_underdog_lines import scrape_nba_lines
from utils.odds_and_lines_utils.nhl.scrape_nhl_underdog_lines import scrape_nhl_lines
app = Flask(__name__)

@app.route('/')
def sports():
     return render_template('sports.html')

@app.route('/nba')
def nba():
    return render_template('nba.html')

@app.route('/nhl')
def nhl():
    return render_template('nhl.html')

@app.route('/get_nba_data', methods=['POST'])
def get_data():
    get_betonline_odds.get_nba_betonline_odds()
    scrape_nba_lines()
    data = find_matches_nba()
    return jsonify(data)

@app.route('/get_nhl_data', methods=['POST'])
def get_nhl_data():
    get_nhl_betonline_odds()
    scrape_nhl_lines()
    return "Success"

@app.route('/get_nba_betonline_odds', methods=['POST'])
def get_nba_betonline_odds():
    get_betonline_odds.get_nba_betonline_odds()
    return "Success"

@app.route('/get_nhl_betonline_odds', methods=['POST'])
def get_nhl_betonline_odds():
    get_betonline_odds.get_nhl_betonline_odds()
    return "Success"

@app.route('/get_nba_underdog_lines', methods=['POST'])
def get_nba_underdog_odds():
    scrape_nba_lines()
    return "Success"

@app.route('/get_nhl_underdog_lines', methods=['POST'])
def get_nhl_underdog_odds():
    scrape_nhl_lines()
    return "Success"

@app.route('/display_nba_odds_and_picks', methods=['POST'])
def display_odds_and_picks():
    data = find_matches_nba()
    return jsonify(data)

@app.route('/display_nhl_odds_and_picks', methods=['POST'])
def display_nhl_odds_and_picks():
    data = find_matches_nhl()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)