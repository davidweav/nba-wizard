import pandas as pd
from betonline_scripts import fetch_betonline_odds
from betonline_scripts import scrape_underdogs

def get_odds_and_lines():
    fetch_betonline_odds()
    scrape_underdogs()
    None

def find_matches():

    try:
        df1 = pd.read_csv('betonline_scripts/betonline-odds/nba_player_odds_2024-02-10.csv')
        df2 = pd.read_csv('betonline_scripts/underdog-lines/player_data_2024-02-10.csv')
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
                        # Compare the property lines between df1 and df2
                        if prop_line_df1 == prop_line_df2:
                            if row1[prop + '_Over'] < row1[prop + '_Under']:
                                odds_value = row1[prop + '_Over']
                                odds_string = 'Over'
                            else:
                                odds_value = row1[prop + '_Under']
                                odds_string = 'Under'
                            # Save the matching lines along with corresponding 'Over' and 'Under' values from df1
                            matching_lines.append({
                                'name': player_name,
                                'proptype': prop,
                                'line': prop_line_df1,
                                'odds': odds_value,
                                'type': odds_string
                            })
                    else:
                        None # no data to compare
    return matching_lines