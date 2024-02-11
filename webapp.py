from flask import Flask, jsonify, render_template, send_from_directory
app = Flask(__name__)

from utils.get_data import return_data
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_data', methods=['POST'])
def get_data():
    # Call your function to retrieve the list of dictionaries
    print("test")
    data = return_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)