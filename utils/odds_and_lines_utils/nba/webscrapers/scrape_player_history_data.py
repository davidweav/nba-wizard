import argparse
import player_data_scraping_utils as utils
import csv
import pandas as pd
from datetime import datetime
from datetime import timedelta
import os

# this script scrapes player history data from basketball-reference.com
# it uses the player_data_scraping_utils.py file to scrape player data

def get_players_from_betonline_odds_csv(current_date):
    players = []
    date_format = "%Y-%m-%d"
    end_date = datetime.strptime("2024-01-22", date_format) # date of the first betonline file
    current_date = datetime.strptime(current_date, date_format)
    while current_date >= end_date:
        try:
            # Read the CSV file and add all players to the list
            df = pd.read_csv(f"odds-lines-data/betonline-odds/betonline_odds_{current_date.strftime(date_format)}.csv")
            for index, row in df.iterrows():
                player_name = row['Player'].lower()
                if player_name not in [player['name'].lower() for player in players]:
                    players.append({"name": player_name, "image": None, "position": None, "shoots": None, "height": None, "weight": None,
                                    "debut": None, "draft-pick": None, "stats": None})
            print(f"Players from betonline file found for {current_date.strftime(date_format)}.")
            current_date -= timedelta(days=1)
        except FileNotFoundError:
            # Sadly, data is not available for every day
            current_date -= timedelta(days=1)
        except KeyError as e:
            print(f"Missing column: {e}")
            exit()
    return players

# function for determining whether the player has data for history already
def player_has_data(player):
    filename = f"player_stats/{player['name'].split(' ')[0]}_{player['name'].split(' ')[1]}_stats.csv"
    return os.path.isfile(filename)

def save_player_stats_to_csv(player, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["date", "season", "game", "age", "team", "opp", "game-result", "min-played", "game-location", "fg", "fga", 
                    "fg-pct",  "fg3", "fg3a", "fg3-pct", "ft", "fta", "ft-pct", "orb", "drb", "trb", "ast",
                    "stl", "blk", "tov", "pf", "points", "game-score", "plus-minus", "game-link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for game_data in player["stats"]:
            writer.writerow(game_data)  # Write each game data to the CSV

def save_all_players_stats(players, driver):
    for player in players:
        # Save player stats to CSV
        player_name_csv = player["name"].replace(" ", "_")
        filename = f"player_stats/{player_name_csv}_stats.csv"
        save_player_stats_to_csv(player, filename, driver)
        print(filename, " saved...")

def main(player_name=None):
    current_date = datetime.now().strftime("%Y-%m-%d")
    if player_name:
        players = [{"name": player_name}]
    else:
        players = get_players_from_betonline_odds_csv(current_date)
        for player in players:
            if player_has_data(player):
                players.remove(player)

    driver = utils.start_driver()
    for player in players:
        player = utils.gather_all_stats_for_player(driver, player)
        print(player["stats"])
        player["name"] = player["name"].title()
        player_name_csv = player["name"].replace(" ", "_")
        filename = f"player_stats/{player_name_csv}_stats.csv"
        save_player_stats_to_csv(player, filename)
        print(f"Player stats saved to {filename}")
    utils.end_driver(driver)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape player history data from basketball-reference.com")
    parser.add_argument("--player", type=str, help="Name of player to scrape")
    parser.add_argument("--all-recent-players", action="store_true", help="Scrape history for all recent players from Betonline CSV")
    args = parser.parse_args()

    if args.player:
        main(args.player)
    elif args.all_recent_players:
        main()
    else:
        print("Please provide either a player's name or use the --all-recent-players option to scrape all recent players from Betonline CSV.")