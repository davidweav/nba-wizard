from flask import Flask, jsonify, render_template, send_from_directory
from utils.find_matches import find_matches, get_odds_and_lines
from utils.scrape_underdogs import do_logic
app = Flask(__name__)

@app.route('/')
def index():
     return render_template('index.html')


@app.route('/get_data', methods=['POST'])
def get_data():
    # Call your function to retrieve the list of dictionaries
    print("test")
    get_odds_and_lines()
    data = find_matches()
    return jsonify(data)

@app.route('/get_betonline_odds', methods=['POST'])
def get_betonline_odds():
    get_odds_and_lines()
    return "Success"

@app.route('/get_underdog_odds', methods=['POST'])
def get_underdog_odds():
    do_logic()
    return "Success"

@app.route('/display_odds_and_picks', methods=['POST'])
def display_odds_and_picks():
    data = find_matches()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)