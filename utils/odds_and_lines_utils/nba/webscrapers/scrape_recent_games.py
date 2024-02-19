from datetime import datetime
import pandas as pd
import csv
import player_data_scraping_utils as utils
import argparse

def get_players_from_betonline_odds_csv(current_date):
    try:
        df = pd.read_csv(f"odds-lines-data/betonline-odds/betonline_odds_{current_date}.csv")
    except KeyError as e:
        print(f"Missing column: {e}")
        exit()
    players = []
    for index, row in df.iterrows():
        player_name = row['Player']
        players.append({"name": player_name, "image": None, "position": None, "shoots": None, "height": None, "weight": None,
                        "debut": None, "draft-pick": None, "stats": None})
    print("Betonline players found.")
    return players

def find_most_recent_data_date(player_name):
    # Determine last date of data
    first_name, last_name = player_name.split(' ') # Assume player name is in format 'First Last'
    first_name = first_name[0].upper() + first_name[1:].lower()
    last_name = last_name[0].upper() + last_name[1:].lower()
    with open(f'player_stats/{first_name}_{last_name}_stats.csv') as f:
        # use pandas to read the csv file
        df = pd.read_csv(f)
        last_row = df.tail(1)
        last_date = last_row['date'].values[0]
        return last_date
    
def get_most_recent_data(player_name):
    player_name = player_name.title()
    last_date = find_most_recent_data_date(player_name)
    driver = utils.start_driver()
    new_player_game_stats = utils.find_new_games(driver, player_name, last_date)
    filename = f"player_stats/{player_name.replace(' ', '_')}_stats.csv"
    df_existing = pd.read_csv(filename)
    df_new_data = pd.DataFrame(new_player_game_stats)
    df_updated = pd.concat([df_existing, df_new_data], ignore_index=True)
    df_updated.to_csv(filename, index=False)
    utils.end_driver(driver)

def main(player_name=None):
    current_date = datetime.now().strftime("%Y-%m-%d")
    if player_name:
        players = [{"name": player_name}]
    else:
        players = get_players_from_betonline_odds_csv(current_date)

    for player in players:
        player_name = player["name"]
        get_most_recent_data(player_name)

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
    


