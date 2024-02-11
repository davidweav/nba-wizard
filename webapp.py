from flask import Flask, jsonify, render_template, send_from_directory
from betonline_scripts.find_matches import find_matches, get_odds_and_lines
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

if __name__ == '__main__':
    app.run(debug=True)