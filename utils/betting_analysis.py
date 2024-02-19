from genericpath import isfile
import pandas as pd
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def get_player_stats(player_name):
    player_name = player_name.replace(' ', '_')
    filename = f"player_stats/{player_name}_stats.csv"
    if os.path.isfile(filename):
        return pd.read_csv(filename)
    else:
        # print(f"No stats file found for {player_name}, with filename {filename}")
        return None

prop_value = {'Points': "fg", 'Rebounds': "trb", 'Assists': "ast", 'Threes': "fg3"}

def analyze_bets(start_date):
    date = start_date
    results = {}
    while True:
        filename = f"odds-lines-data/betonline/nba/nba_betonline_odds_{date.strftime('%Y-%m-%d')}.csv"
        if date > datetime.now():
            break
        if not os.path.isfile(filename):
            date += timedelta(days=1)
            continue
        betonline_data_pd = pd.read_csv(filename)
        for index, row in betonline_data_pd.iterrows():
            player_name = row['Player']
            player_stats_pd = get_player_stats(player_name)
            if player_stats_pd is not None: # check if the player's stats have been scraped
                # get the player's stats for the specified date
                player_game_stats = player_stats_pd[player_stats_pd['date'] == date.strftime('%Y-%m-%d')]
                if not player_game_stats.empty: # ensure that player stats have been scraped for the specified date
                    player_game_stats = player_game_stats.iloc[0]  # get the first (and only) row
                    for prop_type in ['Points', 'Rebounds', 'Assists', 'Threes']:
                        line = row[f'{prop_type}_Line']
                        if not pd.isna(line):  # check if the line exists
                            actual = player_game_stats[prop_value[prop_type]]
                            win_over_under = 'Over' if actual > line else 'Under'
                            loss_over_under = 'Over' if actual < line else 'Under'
                            win_odds = row[f'{prop_type}_{win_over_under}']
                            loss_odds = row[f'{prop_type}_{loss_over_under}']
                            diff = abs(actual - line)
                            if player_name not in results:
                                results[player_name] = {}
                            results[player_name][f'{prop_type}_{date.strftime("%Y-%m-%d")}'] = {'result': win_over_under, 'win-odds': win_odds, 'diff': diff, 'miss': loss_over_under, 'miss-odds': loss_odds}
                            print(results[player_name][f'{prop_type}_{date.strftime("%Y-%m-%d")}'])
        date += timedelta(days=1)
    return results

def graph_hit_percentage(results):
    hit_counts = {}
    miss_counts = {}

    for player in results.values():
        for game in player.values():
            win_odds = game['win-odds']
            miss_odds = game['miss-odds']
            implied_probability = round(abs(win_odds) / (abs(win_odds) + 100) * 100, 2)
            if win_odds not in hit_counts:
                hit_counts[win_odds] = 0
            hit_counts[win_odds] += 1
            if miss_odds not in miss_counts:
                miss_counts[miss_odds] = 0

    total_counts = {}
    for odds in set(hit_counts) | set(miss_counts):
        total_counts[odds] = hit_counts.get(odds, 0) + miss_counts.get(odds, 0)

    # Calculate hit percentage
    hit_percentage = {}
    for odds, total_count in total_counts.items():
        hit_percentage[odds] = hit_counts.get(odds, 0) / total_count if total_count > 0 else 0
    
    
    sorted_keys = sorted(hit_percentage.keys())
    sorted_keys.reverse()

    # Fit a curve (polynomial regression)
    x = np.array(sorted_keys)
    y = np.array([hit_percentage[key] for key in sorted_keys])
    coefficients = np.polyfit(x, y, 3)
    polynomial = np.poly1d(coefficients)
    y_curve = polynomial(x)
    

    # Plotting hit percentage
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(sorted_keys)), [hit_percentage[key] for key in sorted_keys], color='skyblue')
    # plt.plot(x, y_curve, color='red', label='best fit curve', linewidth=2)
    plt.xlabel('Negative Odds Value')
    plt.ylabel('Hit Percentage')
    plt.title('Percentage of Bets that Hit at Negative Odds Values')
    plt.xticks(range(int(min(x)), int(max(x)), 10), rotation=45)

    

    plt.legend()
    plt.tight_layout()
    plt.show()

# Call the function with the results dictionary

# Usage:
results = analyze_bets(datetime(2024, 1, 22))
graph_hit_percentage(results)
