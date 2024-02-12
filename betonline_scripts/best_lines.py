import csv
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")

# Function to read player odds data from CSV file
def read_player_odds_data(csv_file_path):
    player_odds_data = {}
    with open(csv_file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            player_name = row["Player"]
            odds_data = {key: float(value) if value else None for key, value in row.items() if key != "Player"}
            player_odds_data[player_name] = odds_data
    return player_odds_data

def reorder(print_statements):
    odds_values = [int(statement.split(" - ")[-1].split('.')[0]) for statement in print_statements]
    sorted_statements = [statement for _, statement in sorted(zip(odds_values, print_statements))]
    return sorted_statements

# Function to find and print all values between -133 and -155
def print_odds_between_range(player_odds_data):
    print_statements = []
    for player, odds_data in player_odds_data.items():
        for market_type, odds_value in odds_data.items():
            if odds_value is not None and -155 <= odds_value <= -133:
                line_type = market_type.replace('_Over', '_Line').replace('_Under', '_Line')
                line_value = odds_data.get(line_type)
                print_statements.append((player, market_type, line_value, odds_value))
    sorted_statements = sorted(print_statements, key=lambda x: x[-1])
    for player, market_type, line_value, odds_value  in sorted_statements:
        print(f"{player:<20} {market_type:<20} {line_value:<10} {odds_value}")

# File path for the NHL CSV file
csv_file_path_nhl = f"betonline_scripts/betonline_odds/nhl_player_odds_{current_date}.csv"
csv_file_path_nba = f"betonline_scripts/betonline_odds/nba_player_odds_{current_date}.csv"

# Read player odds data from the NHL CSV file
player_odds_data_nhl = read_player_odds_data(csv_file_path_nhl)
player_odds_data_nba = read_player_odds_data(csv_file_path_nba)

# Print the top 20 best odds for NHL
print_odds_between_range(player_odds_data_nba)
# print_odds_between_range(player_odds_data_nhl)
  