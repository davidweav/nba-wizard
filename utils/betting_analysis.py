from genericpath import isfile
import pandas as pd
import os

import os
import pandas as pd
from datetime import datetime, timedelta

def get_player_stats(player_name):
    filename = f"player_stats/{player_name}_stats.csv"
    if os.path.isfile(filename):
        return pd.read_csv(filename)
    else:
        print(f"No stats file found for {player_name}")
        return None

def analyze_bets(start_date):
    date = start_date
    results = {}
    while True:
        filename = f"betonline_odds_{date.strftime('%Y-%m-%d')}.csv"
        if not os.path.isfile(filename):
            break
        betonline_data = pd.read_csv(filename)
        for index, row in betonline_data.iterrows():
            player_name = row['Player']
            player_stats = get_player_stats(player_name)
            if player_stats is not None:
                player_game_stats = player_stats[player_stats['date'] == date.strftime('%Y-%m-%d')]
                if not player_game_stats.empty:
                    player_game_stats = player_game_stats.iloc[0]  # get the first (and only) row
                    for prop_type in ['Points', 'Rebounds', 'Assists', 'Threes']:
                        line = row[f'{prop_type}_Line']
                        if not pd.isna(line):  # check if the line exists
                            actual = player_game_stats[prop_type.lower()]
                            over_under = 'Over' if actual > line else 'Under'
                            odds = row[f'{prop_type}_{over_under}']
                            if player_name not in results:
                                results[player_name] = {}
                            results[player_name][f'{prop_type}_{date.strftime("%Y-%m-%d")}'] = {'over_under': over_under, 'odds': odds}
        date += timedelta(days=1)
    return results

# Usage:
results = analyze_bets(datetime(2024, 1, 22))
print(results)