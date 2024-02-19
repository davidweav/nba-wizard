import pandas as pd
from datetime import datetime
import json

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
    properties = ['Saves', 'Shots', 'Goals']

    for prop in properties:
        prop_line_betonline = f'{prop}_Line'

        # Iterate over each row in the betonline DataFrame
        for index, row1 in df1.iterrows():
            player_name = row1['Player']
            prop_line_betonline_value = row1[prop_line_betonline]


            for index, row2 in df2.iterrows():
                prop_lines_underdog = [row2[f'{prop}H'], row2[f'{prop}L'], row2[f'{prop}C']]
                    
                # Check if the property line from BetOnline matches any of the property lines from Underdog
                if prop_line_betonline_value in prop_lines_underdog:
                    # Calculate additional information
                    odds = row1[f'{prop}_Over'] if row1[f'{prop}_Over'] < row1[f'{prop}_Under'] else row1[f'{prop}_Under']
                    odds_string = 'Over' if row1[f'{prop}_Over'] < row1[f'{prop}_Under'] else 'Under'
                    implied_probability = round(abs(odds) / (abs(odds) + 100) * 100, 2)
                    multiplier = row2['Multiplier']
                    
                    # Save the matching lines along with additional information
                    matching_lines.append({
                        'name': player_name,
                        'prop': prop,
                        'line': prop_line_betonline_value,
                        'odds': odds,
                        'type': odds_string,
                        'implied_probability': implied_probability,
                        'multiplier': multiplier
                    })
    with open(f'odds-lines-data/matching-lines/nhl/nhl_matching_lines_{current_date}.txt', 'w') as matching_lines_file:
        json.dump(matching_lines, matching_lines_file, indent=2)
    return matching_lines