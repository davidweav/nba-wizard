import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import time
from datetime import datetime
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import csv
import re

ublock_path = "chrome-extensions\AdBlock.crx"
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_argument("--disable-logging")
# options.add_argument('load-extension=' + ublock_path)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()

def remove_ads(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.adblock.primis")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fs-sticky-slot-element")))
    except TimeoutException:
        print("Ads did not load in time")
        return
    ads = driver.find_elements(By.CSS_SELECTOR, "div.adblock.primis")
    ads += driver.find_elements(By.CSS_SELECTOR, "div.fs-sticky-slot-element")
    for ad in ads:
        driver.execute_script("arguments[0].remove();", ad)

def get_team_code(team_name):
    team_mapping = {
    'ATL': 1, 'BOS': 2, 'BRK': 3, 'CHO': 4, 'CHI': 5,
    'CLE': 6, 'DAL': 7, 'DEN': 8, 'DET': 9, 'GSW': 10,
    'HOU': 11, 'IND': 12, 'LAC': 13, 'LAL': 14, 'MEM': 15,
    'MIA': 16, 'MIL': 17, 'MIN': 18, 'NOP': 19, 'NYK': 20,
    'OKC': 21, 'ORL': 22, 'PHI': 23, 'PHO': 24, 'POR': 25,
    'SAC': 26, 'SAS': 27, 'TOR': 28, 'UTA': 29, 'WAS': 30
    }
    return team_mapping.get(team_name, -1)

def get_position_abbreviation(position):
    position_mapping = {
        "Point Guard": "PG", "Shooting Guard": "SG", "Small Forward": "SF", "Power Forward": "PF", "Center": "C"
    }
    return position_mapping.get(position, "N/A")

def get_player_info(driver):
    meta_info_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[id='meta']")))
    try:
        meta_more_button = meta_info_div.find_element(By.CSS_SELECTOR, "button[id='meta_more_button']")
        meta_more_button.click()
    except NoSuchElementException:
        pass
    image_src = meta_info_div.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
    p_elements = meta_info_div.find_elements(By.CSS_SELECTOR, "p")
    full_text = ""
    for p_element in p_elements:
        full_text += "\n" + p_element.text
    # Parse required info
    position = re.search(r'Position: (.*?) ▪', full_text).group(1)
    position = get_position_abbreviation(position)
    shoots = re.search(r'Shoots: (.*?)\n', full_text).group(1)
    shoots = "R" if "Right" in shoots else "L"
    height = re.search(r'(\d+-\d+), \d+lb', full_text).group(1)
    feet, inches = map(int, height.split('-'))
    height_in_inches = feet * 12 + inches
    weight = re.search(r'\d+-\d+, (\d+)lb', full_text).group(1)
    debut = re.search(r'NBA Debut: (.*?)\n', full_text).group(1)
    debut_date = datetime.strptime(debut, "%B %d, %Y")
    debut = debut_date.strftime("%Y-%m-%d")
    draft_pick = re.search(r'Draft: .*? \(\d+(?:st|nd|rd|th) pick, (\d+)(?:st|nd|rd|th) overall\)', full_text).group(1)
    return image_src, position, shoots, height_in_inches, weight, debut, draft_pick
        

def get_player_seasons_links(driver):
    driver.execute_script("window.scrollTo(0, 1000)")
    # Get player links
    player_seasons_stat_table = driver.find_element(By.CSS_SELECTOR, "table.stats_table.sortable.row_summable.now_sortable#per_game[data-cols-to-freeze='1,3']")
    all_seasons_table = player_seasons_stat_table.find_elements(By.CSS_SELECTOR, "th[data-stat='season'] a")
    season_links = []
    for i in all_seasons_table:
        season_links.append(i.get_attribute("href"))
    print("Player season links found.")
    return season_links

def get_stats(driver, URL):
    driver.get(URL)
    remove_ads(driver)
    driver.execute_script("window.scrollTo(0, 1500)")
    data_rows = driver.find_elements(By.CSS_SELECTOR, "tr[data-row]")
    game_data_list = []
    game = 0
    for data_row in data_rows:
        if data_row.get_attribute("class") != "thead":
            season = URL.split('/')[-1]
            date = data_row.find_element(By.CSS_SELECTOR, "td[data-stat='date_game']").text
            game_link = data_row.find_element(By.CSS_SELECTOR, "a").get_attribute("href"),
            age = float(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='age']").text.replace("-", "."))
            team = get_team_code(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='team_id']").text)
            opp = get_team_code(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='opp_id']").text)
            game_result = int(data_row.find_element(By.CSS_SELECTOR, 'td[data-stat="game_result"]').get_attribute("csk"))
            game_location = data_row.find_element(By.CSS_SELECTOR, "td[data-stat='game_location']").text
            game_location = 0 if '@' in game_location else 1
            try:
                minutes_played_text = data_row.find_element(By.CSS_SELECTOR, "td[data-stat='mp']").text
            except NoSuchElementException:
                game_data = {
                "date": None, "season": season, "game": game, "age": age, "team": team, "opp": opp, "game-result": game_result, "min-played": 0,
                "game-location": game_location, "fg": 0, "fga": 0, "fg-pct": 0, "fg3": 0, "fg3a": 0, "fg3-pct": 0, "ft": 0, "fta": 0,
                "ft-pct": 0, "orb": 0, "drb": 0, "trb": 0, "ast": 0, "stl": 0, "blk": 0, "tov": 0, "pf": 0, "points": 0,
                "game-score": 0, "plus-minus": 0, "game-link": game_link
                }
                game_data_list.append(game_data)
                game += 1
                print(game)
                continue
            minutes_played_split = minutes_played_text.split(":")
            minutes = int(minutes_played_split[0])
            seconds = int(minutes_played_split[1])
            mp = round(minutes + (seconds / 60.0), 3)
            fg = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='fg']").text)
            fga = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='fga']").text)
            fg_pct = data_row.find_element(By.CSS_SELECTOR, "td[data-stat='fg_pct']")
            fg_pct = round(float(fg_pct.text), 3) if fg_pct.text else 0.0
            fg3 = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='fg3']").text)
            fg3a = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='fg3a']").text)
            fg3_pct_element = data_row.find_element(By.CSS_SELECTOR, "td[data-stat='fg3_pct']")
            fg3_pct = round(float(fg3_pct_element.text), 3) if fg3_pct_element.text else 0.0
            ft = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='ft']").text)
            fta = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='fta']").text)
            ft_pct_element = data_row.find_element(By.CSS_SELECTOR, "td[data-stat='ft_pct']")
            ft_pct = round(float(ft_pct_element.text), 3) if ft_pct_element.text else 0.0
            orb = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='orb']").text)
            drb = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='drb']").text)
            trb = orb + drb
            ast = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='ast']").text)
            stl = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='stl']").text)
            blk = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='blk']").text)
            tov = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='tov']").text)
            pf = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='pf']").text)
            points = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='pts']").text)
            game_score = round(float(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='game_score']").text), 3)
            plus_minus = int(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='plus_minus']").text)
            game_data = {
                "date": date, "season": season, "game": game, "age": age, "team": team, "opp": opp, "game-result": game_result, "min-played": mp,
                "game-location": game_location, "fg": fg, "fga": fga, "fg-pct": fg_pct, "fg3": fg3, "fg3a": fg3a, "fg3-pct": fg3_pct, "ft": ft,
                "fta": fta, "ft-pct": ft_pct, "orb": orb, "drb": drb, "trb": trb, "ast": ast, "stl": stl, "blk": blk, "tov": tov, "pf": pf,
                "points": points, "game-score": game_score, "plus-minus": plus_minus, "game-link": game_link
            }
            game_data_list.append(game_data)
            game += 1
            print(game)
    print(len(game_data_list))
    return game_data_list

def get_players_from_betonline():
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        df = pd.read_csv(f"betonline_scripts/betonline-odds/betonline_odds_{current_date}.csv")
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

def get_player_stats(driver, player):
    driver.get("https://www.basketball-reference.com/players")
    remove_ads(driver)
    search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='search']")))
    search_box.send_keys(player["name"])
    search_box.submit()
    search_result = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.search-item-name")))
    search_result_link = search_result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
    driver.get(search_result_link)
    player["image"], player["position"], player["shoots"], player["height"], player["weight"], player["debut"], player["draft-pick"] = get_player_info(driver)
    time.sleep(1)
    player_season_links = get_player_seasons_links(driver)
    all_player_game_stats = []
    for URL in player_season_links:
        all_player_game_stats.extend(get_stats(driver, URL))
    print(len(all_player_game_stats), " more games found.")
    return all_player_game_stats

def save_player_stats_to_csv(player, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["date", "season", "game", "age", "team", "opp", "game-result", "min-played", "game-location", "fg", "fga", 
                    "fg-pct",  "fg3", "fg3a", "fg3-pct", "ft", "fta", "ft-pct", "orb", "drb", "trb", "ast",
                    "stl", "blk", "tov", "pf", "points", "game-score", "plus-minus", "game-link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for game_data in player["stats"]:
            print(game_data)
            writer.writerow(game_data)  # Write each game data to the CSV

def save_all_players_stats(players):
  for player in players:
        all_player_game_stats = get_player_stats(driver, player)  # Get player stats
        player["stats"] = all_player_game_stats
        player_name_csv = player["name"].replace(" ", "_")
        filename = f"player_stats/{player_name_csv}_stats.csv"
        save_player_stats_to_csv(player, filename)
        print(filename, " saved...")

players = get_players_from_betonline()
save_all_players_stats(players)
driver.quit()
