import requests
import json
import csv
from datetime import datetime

sport_nba = "basketball_nba"
regions = "us"
odds_format = "american"
bookmaker_key = "betonlineag"

desired_markets_nba = [
    "player_points", "player_rebounds", "player_points_rebounds_assists",
    "player_assists", "player_threes"
]

def get_player_props_nba(event_id, player_odds_dict_nba, api_key):
    markets_str = ",".join(desired_markets_nba)
    url_nba = f"https://api.the-odds-api.com/v4/sports/{sport_nba}/events/{event_id}/odds?apiKey={api_key}&regions={regions}&markets={markets_str}&oddsFormat={odds_format}&bookmakers={bookmaker_key}"
    url_williamhill = f"https://api.the-odds-api.com/v4/sports/{sport_nba}/events/{event_id}/odds?apiKey={api_key}&regions={regions}&markets={markets_str}&oddsFormat={odds_format}&bookmakers=williamhill_us"

    print(url_nba)
    response = requests.get(url_nba)
    # print(url_nba)
    if response.status_code == 401:
        print("Request quoata has been reached for", api_key)
        return False
    player_props_data_nba = response.json()
    if not player_props_data_nba.get('bookmakers'):
        player_props_data_nba = requests.get(url_williamhill).json()
        # print("Request URL:", url_williamhill)
        if response.status_code == 401:
            print("Request quoata has been reached for", api_key)
            return False

    try:
        for market in player_props_data_nba['bookmakers'][0]['markets']:
            market_key = market['key']
            market_type = market_key.split('_')[1].capitalize()  # Assuming the format is always "player_{type}"
            for outcome in market['outcomes']:
                player_name = outcome['description']
                over_odds = outcome['price'] if outcome['name'] == 'Over' else None
                under_odds = outcome['price'] if outcome['name'] == 'Under' else None
                line_value = outcome.get('point')  # Extract the line value

                if player_name in player_odds_dict_nba:
                    # Update existing values while preserving the existing ones
                    player_odds_dict_nba[player_name][market_type]["Over"] = over_odds if over_odds is not None else player_odds_dict_nba[player_name][market_type]["Over"]
                    player_odds_dict_nba[player_name][market_type]["Under"] = under_odds if under_odds is not None else player_odds_dict_nba[player_name][market_type]["Under"]
                    player_odds_dict_nba[player_name][market_type]["Line"] = line_value  # Include the line value
                else:
                    # Create a new entry in the dictionary
                    player_odds_dict_nba[player_name] = {
                        "Points": {"Over": None, "Under": None, "Line": None},
                        "Rebounds": {"Over": None, "Under": None, "Line": None},
                        "Assists": {"Over": None, "Under": None, "Line": None},
                        "PointsReboundsAssists": {"Over": None, "Under": None, "Line": None},
                        "Threes": {"Over": None, "Under": None, "Line": None}
                    }
                    # Update odds values based on the market
                    player_odds_dict_nba[player_name][market_type]["Over"] = over_odds
                    player_odds_dict_nba[player_name][market_type]["Under"] = under_odds
                    player_odds_dict_nba[player_name][market_type]["Line"] = line_value
    except Exception as e:
        print(e)
        return True

def fetch_nba_pp(api_key):
    player_odds_dict_nba = {}

    current_date = datetime.now().strftime("%Y-%m-%d")

    input_file_path_nba = f"betonline_scripts/events/nba_games_{current_date}.json"
    output_csv_file_path_nba = f"betonline_scripts/betonline-odds/nba_player_odds_{current_date}.csv"

    with open(input_file_path_nba, "r") as json_file_nba:
        games_info_nba = json.load(json_file_nba)

    for idx_nba, game_info_nba in games_info_nba.items():
        event_id_nba = game_info_nba.get("event_id")

        if event_id_nba:
            player_props_nba = get_player_props_nba(event_id_nba, player_odds_dict_nba, api_key=api_key)
            if player_props_nba == False:
                return False

    prop_types_nba = set()
    for player_name_nba, prop_data_nba in player_odds_dict_nba.items():
        for prop_type_nba, odds_data_nba in prop_data_nba.items():
            for over_under_nba in ["Over", "Under", "Line"]:
                column_name_nba = f"{prop_type_nba}_{over_under_nba}"
                prop_types_nba.add(column_name_nba)

    with open(output_csv_file_path_nba, "w") as csv_file_nba:
        writer_nba = csv.DictWriter(csv_file_nba, fieldnames=["Player"] + sorted(prop_types_nba))
        
        # Write headers
        writer_nba.writeheader()

        # Write data rows
        for player_name_nba, prop_data_nba in player_odds_dict_nba.items():
            row_data_nba = {"Player": player_name_nba}
            for prop_type_nba, odds_data_nba in prop_data_nba.items():
                for over_under_nba in ["Over", "Under", "Line"]:
                    column_name_nba = f"{prop_type_nba}_{over_under_nba}"
                    row_data_nba[column_name_nba] = odds_data_nba[over_under_nba]
            writer_nba.writerow(row_data_nba)
    return True
