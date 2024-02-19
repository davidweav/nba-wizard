from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import re
import csv
import time

def start_driver():
    # This function starts the webdriver and returns the driver object
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    return driver

def end_driver(driver):
    # This function ends the webdriver
    driver.quit()

def remove_ads(driver):
    # This function removes ads from the webpage
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
    # This dictionary maps the team name to a unique integer. This is useful for AI models
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

def navigate_to_player_page(driver, player_name):
    print(f"Navigating to {player_name}'s page...")
    driver.get("https://www.basketball-reference.com/players")
    remove_ads(driver)
    search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='search']")))
    search_box.send_keys(player_name)
    search_box.submit()
    search_result = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.search-item-name")))
    search_result_link = search_result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
    driver.get(search_result_link)

def get_player_info(driver, player_name):
    print(f"Getting {player_name}'s info...")
    navigate_to_player_page(driver, player_name)
    # find the meta info div and click the "more info" button if it exists
    meta_info_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[id='meta']")))
    try:
        meta_more_button = meta_info_div.find_element(By.CSS_SELECTOR, "button[id='meta_more_button']")
        meta_more_button.click()
    except NoSuchElementException:
        pass
    # find image location
    image_src = meta_info_div.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
    # get all player info (just the entire text of the div, then parse it with regex later on)
    p_elements = meta_info_div.find_elements(By.CSS_SELECTOR, "p")
    full_text = ""
    for p_element in p_elements:
        full_text += "\n" + p_element.text
    # Parse required info using regular expressions
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

def get_player_seasons_links(driver, player_name):
    print(f"Getting {player_name}'s season links...")
    navigate_to_player_page(driver, player_name)
    driver.execute_script("window.scrollTo(0, 1000)")
    # Get player links
    player_seasons_stat_table = driver.find_element(By.CSS_SELECTOR, "table.stats_table.sortable.row_summable.now_sortable#per_game[data-cols-to-freeze='1,3']")
    all_seasons_table = player_seasons_stat_table.find_elements(By.CSS_SELECTOR, "th[data-stat='season'] a")
    season_links = []
    for i in all_seasons_table:
        season_link = i.get_attribute("href")
        if season_link not in season_links:
            season_links.append(season_link)
    print("Player season links found.")
    return season_links

def find_stat(data_row, css_search):
    try:
        stat = data_row.find_element(By.CSS_SELECTOR, css_search).text
        if stat == '':
            return "0"
        return stat
    except NoSuchElementException:
        if css_search in "td[data-stat='fg_pct":
            return "0.0"
        return "0"

def get_data_row_stats(data_row, game, season):
    # get all the data from the row
    date = data_row.find_element(By.CSS_SELECTOR, "td[data-stat='date_game']").text
    game_link = data_row.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
    age = float(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='age']").text.replace("-", "."))
    team = get_team_code(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='team_id']").text)
    opp = get_team_code(data_row.find_element(By.CSS_SELECTOR, "td[data-stat='opp_id']").text)
    game_result = int(data_row.find_element(By.CSS_SELECTOR, 'td[data-stat="game_result"]').get_attribute("csk"))
    game_location = data_row.find_element(By.CSS_SELECTOR, "td[data-stat='game_location']").text
    game_location = 0 if '@' in game_location else 1
    try:
        # if the player did not play in the game, then the minutes played will be empty
        # and all other stats will be 0
        minutes_played_text = data_row.find_element(By.CSS_SELECTOR, "td[data-stat='mp']").text
    except NoSuchElementException:
        # create a dictionary with all the data and no stats since the player did not play.
        # this is a DNP, and is necessary for AI models to understand that the player did not play
        game_data = {
        "date": date, "season": season, "game": game, "age": age, "team": team, "opp": opp, "game-result": game_result, "min-played": 0,
        "game-location": game_location, "fg": 0, "fga": 0, "fg-pct": 0, "fg3": 0, "fg3a": 0, "fg3-pct": 0, "ft": 0, "fta": 0,
        "ft-pct": 0, "orb": 0, "drb": 0, "trb": 0, "ast": 0, "stl": 0, "blk": 0, "tov": 0, "pf": 0, "points": 0,
        "game-score": 0, "plus-minus": 0, "game-link": game_link
        }
        return game_data
    minutes_played_split = minutes_played_text.split(":")
    minutes = int(minutes_played_split[0])
    seconds = int(minutes_played_split[1])
    mp = round(minutes + (seconds / 60.0), 3)
    fg = int(find_stat(data_row, "td[data-stat='fg']"))
    fga = int(find_stat(data_row, "td[data-stat='fga']"))
    if fga > 0:
        fg_pct = round(fg / fga, 3)
    else:
        fg_pct = 0.0
    fg3 = int(find_stat(data_row, "td[data-stat='fg3']"))
    fg3a = int(find_stat(data_row, "td[data-stat='fg3a']"))
    if fg3 > 0:
        fg3_pct = round(fg3 / fg3a, 3)
    else:
        fg3_pct = 0.0
    ft = int(find_stat(data_row, "td[data-stat='ft']"))
    fta = int(find_stat(data_row, "td[data-stat='fta']"))
    if fta > 0:
        ft_pct = round(ft / fta, 3)
    else:
        ft_pct = 0.0
    orb = int(find_stat(data_row, "td[data-stat='orb']"))
    drb = int(find_stat(data_row, "td[data-stat='drb']"))
    trb = orb + drb
    ast = int(find_stat(data_row, "td[data-stat='ast']"))
    stl = int(find_stat(data_row, "td[data-stat='stl']"))
    blk = int(find_stat(data_row, "td[data-stat='blk']"))
    tov = int(find_stat(data_row, "td[data-stat='tov']"))
    pf = int(find_stat(data_row, "td[data-stat='pf']"))
    points = int(find_stat(data_row, "td[data-stat='pts']"))
    game_score = round(float(find_stat(data_row, "td[data-stat='game_score']")), 3)
    plus_minus = int(find_stat(data_row, "td[data-stat='plus_minus']"))
    # create a dictionary with all the data
    game_data = {
        "date": date, "season": season, "game": game, "age": age, "team": team, "opp": opp, "game-result": game_result, "min-played": mp,
        "game-location": game_location, "fg": fg, "fga": fga, "fg-pct": fg_pct, "fg3": fg3, "fg3a": fg3a, "fg3-pct": fg3_pct, "ft": ft,
        "fta": fta, "ft-pct": ft_pct, "orb": orb, "drb": drb, "trb": trb, "ast": ast, "stl": stl, "blk": blk, "tov": tov, "pf": pf,
        "points": points, "game-score": game_score, "plus-minus": plus_minus, "game-link": game_link
    }
    return game_data

def get_season_stats(driver, season_link):
    driver.get(season_link)
    remove_ads(driver)
    driver.execute_script("window.scrollTo(0, 1500)")
    data_rows = driver.find_elements(By.CSS_SELECTOR, "tr[data-row]")
    game_data_list = []
    game = 0
    season = season_link.split('/')[-1]
    for data_row in data_rows:
        if data_row.get_attribute("class") != "thead":
            game_data = get_data_row_stats(data_row, game, season)
            game_data_list.append(game_data)
            game += 1
            print(season, game, "game acquired.")
    print(len(game_data_list))
    return game_data_list

def gather_all_stats_for_player(driver, player):
    print(f"Gathering all stats for {player['name']}...")
    player["image"], player["position"], player["shoots"], player["height"], player["weight"], player["debut"], player["draft-pick"] = get_player_info(driver, player["name"])
    player_season_links = get_player_seasons_links(driver, player["name"])
    all_player_game_stats = []
    for season_link in player_season_links:
        all_player_game_stats.extend(get_season_stats(driver, season_link))
    player["stats"] = all_player_game_stats
    return player

def find_new_games(driver, player_name, last_date):
    games_to_be_appended = []
    # this function uses the last date of data to navigate to the season that contains that date
    player_season_links = get_player_seasons_links(driver, player_name)
    # determine link that contains the last date of data
    date_found = False
    for player_season_link in reversed(player_season_links):
        driver.get(player_season_link)
        print(player_season_link)
        remove_ads(driver)
        driver.execute_script("window.scrollTo(0, 1500)")
        data_rows = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr[data-row]")))
        # look for the date in the season in reverse order
        print(f"Need to find {last_date}...")
        game_count = 0
        for data_row in data_rows:
            game_count += 1
        for data_row in reversed(data_rows):
            if data_row.get_attribute("class") != "thead":
                season = player_season_link.split('/')[-1]
                game_data = get_data_row_stats(data_row, game_count, season)
                game_date = game_data["date"]
                print(f"Checking {game_date}...")
                if game_date == last_date:
                    games_to_be_appended.append(game_data)
                    date_found = True
                    break # stop looking for date in more seasons
                games_to_be_appended.append(game_data)
        # if date wasn't found in this season, then continue to the next season
        # this means that multiple seasons will need to be checked
        if date_found:
            break
    # Now that the games to be appended have been found, return    
    games_to_be_appended = reversed(games_to_be_appended)
    return games_to_be_appended
