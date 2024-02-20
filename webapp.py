from flask import Flask, jsonify ,render_template, request
from utils.find_matches import find_matches_nba, find_matches_nhl
import utils.odds_and_lines_utils.get_betonline_odds as get_betonline_odds
from utils.odds_and_lines_utils.nba.scrape_nba_underdog_lines import scrape_nba_lines
from utils.odds_and_lines_utils.nhl.scrape_nhl_underdog_lines import scrape_nhl_lines
from utils.expected_value import calculate_expected_value
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

@app.route('/calculate_expected_value', methods=['POST'])
def calculate_expected_value():
    data = request.get_json()
    probabilities = data['probabilities']
    multipliers = data['multipliers']
    bet_amount = data['betAmount']
    # EV = P(win) x Payout - P(loss) x Bet
    # Calculate the product of probabilities (P(win))
    prob_win_combined = 1
    for prob in probabilities:
        prob = prob / 100
        prob_win_combined *= prob
    # (P(loss))
    prob_lose = 1 - prob_win_combined
    # Calculate the product of multipliers (Payout)
    expected_payout = 3
    for multiplier in multipliers:
        expected_payout *= multiplier
    # Calculate and return the expected value
    ev = prob_win_combined * expected_payout * bet_amount - prob_lose * bet_amount
    # print(ev)
    return jsonify({"expectedValue": ev})

if __name__ == '__main__':
    app.run(debug=True)