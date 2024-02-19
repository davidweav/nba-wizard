from numpy import NaN
import pandas as pd
from datetime import datetime
import json
import time
import math

def find_matches_nba():
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        df1 = pd.read_csv(f'odds-lines-data/betonline-odds/nba_betonline_odds_{current_date}.csv')
        df2 = pd.read_csv(f'odds-lines-data/underdog-lines/nba_underdog_lines_{current_date}.csv')
    except KeyError as e:
        print(f"Missing column: {e}")
        exit()
    matching_lines = []
    properties = ['Assists', 'PointsReboundsAssists', 'Points', 'Rebounds', 'Threes']

    for index, row1 in df1.iterrows():
        player_name = row1['Player']
        
        # Find the corresponding row in the second DataFrame
        matching_row = df2[df2['Name'] == player_name]
        
        # Check if the matching row exists
        if not matching_row.empty:
            # Iterate over the properties
            for prop in properties:
                if prop + '_Line' in row1 and prop + '_Line' in matching_row:
                    prop_line_df1 = row1[prop + '_Line']
                    prop_line_df2 = matching_row[prop + '_Line'].iloc[0]
                    
                    # Check if any required value is missing
                    if pd.notna(prop_line_df1) and pd.notna(prop_line_df2):
                        # Remove the possible 's' from underdogs prop
                        is_underdog_prop_scorcher = False
                        if 's' in str(prop_line_df2):
                            prop_line_df2 = prop_line_df2[:-1]
                            is_underdog_prop_scorcher = True
                        
                        # Compare the property lines between df1 and df2
                        prop_line_df1, prop_line_df2 = float(prop_line_df1), float(prop_line_df2)
                        if prop_line_df1 == prop_line_df2:
                            if row1[prop + '_Over'] < row1[prop + '_Under']:
                                odds_value = row1[prop + '_Over']
                                odds_string = 'Over'
                            else:
                                odds_value = row1[prop + '_Under']
                                odds_string = 'Under'
                                if is_underdog_prop_scorcher:
                                    continue
                            # Save the matching lines along with corresponding 'Over' and 'Under' values from df1
                            implied_probability = round(abs(odds_value) / (abs(odds_value) + 100) * 100, 2)
                            matching_lines.append({
                                'name': player_name,
                                'proptype': prop,
                                'line': prop_line_df1,
                                'odds': odds_value,
                                'type': odds_string,
                                'implied_probability': implied_probability
                            })
                    else:
                        None # no data to compare
    matching_lines = sorted(matching_lines, key=lambda k: k['odds'])
    matching_lines = [line for line in matching_lines if line['odds'] <= -135]
    with open(f'odds-lines-data/matching-lines/nba/nba_matching_lines_{current_date}.txt', 'w') as matching_lines_file:
        json.dump(matching_lines, matching_lines_file, indent=2)
    return matching_lines

def find_matches_nhl():
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        df1 = pd.read_csv(f'odds-lines-data/betonline/nhl/nhl_odds_{current_date}.csv')
        df2 = pd.read_csv(f'odds-lines-data/underdog-lines/nhl/nhl_underdog_lines_{current_date}.csv')
    except KeyError as e:
        print(f"Missing column: {e}")
        exit()
    matching_lines = []
    properties = ['Shots', 'Points'] # 'Goals', 'Assists', etc. could be added
    for prop in properties:
        prop_line_betonline = f'{prop}_Line' # 'Shots_Line', 'Points_Line', etc.
        # Iterate over each row in the betonline DataFrame
        for index, row1 in df1.iterrows():
            player_name = row1['Player']
            prop_line_betonline_value = row1[prop_line_betonline] # 'Shots_Line' value, 'Points_Line' value, etc.
            row2 = df2.loc[df2['Name'] == player_name]
            if not row2.empty and isinstance(prop_line_betonline_value, float) and not math.isnan(prop_line_betonline_value):
                prop_line_underdog_C = str(row2[f'{prop}C'].iloc[0])
                prop_line_underdog_H = str(row2[f'{prop}H'].iloc[0])
                prop_line_underdog_L = str(row2[f'{prop}L'].iloc[0])
                prop_lines_underdog = [prop_line_underdog_H, prop_line_underdog_L, prop_line_underdog_C]
                # print(prop_line_underdog_C, prop_line_underdog_H, prop_line_underdog_L, prop_line_betonline_value)
                # Check if the property line from BetOnline matches any of the property lines from Underdog
                prop_line_betonline_string = str(prop_line_betonline_value)
                prop_lines_underdog_strings = []
                matching_line_exists = False
                for line in prop_lines_underdog:
                    if isinstance(line, float) and math.isnan(line):
                        prop_lines_underdog_strings.append("nan")
                    else:
                        prop_lines_underdog_strings.append(str(line))
                for line in prop_lines_underdog_strings:
                    if prop_line_betonline_string in line:
                        matching_line_exists = True # found a matching line
                if matching_line_exists:
                    # Calculate additional information
                    found_match = False
                    if str(prop_line_underdog_C) != "nan" and prop_line_underdog_C.split("x")[0] in prop_line_betonline_string:
                        found_match = True
                        prop_line_underdog = prop_line_underdog_C
                        odds_string = 'Over' if row1[f'{prop}_Over'] < row1[f'{prop}_Under'] else 'Under'
                        odds = row1[f'{prop}_Over'] if row1[f'{prop}_Over'] < row1[f'{prop}_Under'] else row1[f'{prop}_Under']
                    # Check if the Underdog line for user choice is missing
                    if prop_line_underdog_C == "nan":
                        # Check the higher and lower lines
                        print(row1[f"{prop}_Over"], row1[f"{prop}_Under"], prop_line_underdog_H.split("x")[0], prop_line_underdog_L.split("x")[0], prop_line_betonline_value)
                        line_matches_H = prop_line_underdog_H.split("x")[0] == str(prop_line_betonline_value)
                        over_odds_better_than_under = False
                        if isinstance(row1[f"{prop}_Over"], float) and math.isnan(row1[f"{prop}_Over"]):
                            over_odds_better_than_under = False # no 'Over' odds, so skip checking over
                        elif isinstance(row1[f"{prop}_Under"], float) and math.isnan(row1[f"{prop}_Under"]):
                            over_odds_better_than_under = True # no 'Under' odds, so skip checking under
                        elif row1[f"{prop}_Over"] < row1[f"{prop}_Under"]:
                            over_odds_better_than_under = True # 'Over' odds are better than 'Under' odds
                        print(line_matches_H, over_odds_better_than_under)
                        if line_matches_H and over_odds_better_than_under:
                            # If the line from BetOnline matches the line from Underdog, and the 
                            # 'Over' odds are better than the 'Under' odds, then use the 'Over' line
                            found_match = True
                            prop_line_underdog = prop_line_underdog_H
                            odds_string = "Over"
                            odds = row1[f'{prop}_Over']

                        line_matches_L = prop_line_underdog_L.split("x")[0] == prop_line_betonline_value
                        under_odds_better_than_over = False
                        if isinstance(row1[f"{prop}_Under"], float) and math.isnan(row1[f"{prop}_Under"]):
                            under_odds_better_than_over = False # no 'Under' odds, so skip checking over
                        elif isinstance(row1[f"{prop}_Over"], float) and math.isnan(row1[f"{prop}_Over"]):
                            under_odds_better_than_over = True # no 'Under' odds, so skip checking under
                        elif row1[f"{prop}_Under"] < row1[f"{prop}_Over"]:
                            under_odds_better_than_over = True # 'Under' odds are better than 'Under' odds
                        print(line_matches_L, under_odds_better_than_over)
                        if line_matches_L and under_odds_better_than_over:
                            # Line from BetOnline matches the line from Underdog, and the 'Under' odds 
                            # are better than the 'Over' odds
                            found_match = True
                            prop_line_underdog = prop_line_underdog_L
                            odds_string = "Under"
                            odds = row1[f'{prop}_Under']
                    if found_match:
                        implied_probability = round(abs(odds) / (abs(odds) + 100) * 100, 2)
                        multiplier = prop_line_underdog.split("x")[1]
                        # Save the matching lines along with additional information
                        matching_lines.append({
                            'name': player_name,
                            'proptype': prop,
                            'line': prop_line_betonline_value,
                            'odds': odds,
                            'type': odds_string,
                            'implied_probability': implied_probability,
                            'multiplier': multiplier
                        })
                else:
                    # No matching line found
                    None
    matching_lines = sorted(matching_lines, key=lambda k: k['odds'])
    matching_lines = [line for line in matching_lines if line['odds'] <= -120]
    with open(f'odds-lines-data/matching-lines/nhl/nhl_matching_lines_{current_date}.txt', 'w') as matching_lines_file:
        json.dump(matching_lines, matching_lines_file, indent=2)
    return matching_lines
