import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

from zmq import has

# C: Choice, O: Over, U: Under
# Underdog has over/under, and sometimes only one choice (Over or Under)
FIELDNAMES = ["Name", "PointsH", "PointsL", "PointsC", "ShotsH", "ShotsL", "ShotsC", "BlockedShotsH", "BlockedShotsL", "BlockedShotsC", "GoalsH", "GoalsL", "GoalsC", "AssistsH", "AssistsL", "AssistsC", "PowerPlayPointsH", "PowerPlayPointsL", "PowerPlayPointsC", "FantasyH", "FantasyL", "FantasyC", "SavesH", "SavesL", "SavesC", "GoalsAgainstH", "GoalsAgainstL", "GoalsAgainstC"]

def login(driver):
    username = "ugageeb@gmail.com"
    password = "jbpojerg772@dfbjpjrgSDG"
    driver.get("https://underdogfantasy.com/pick-em/higher-lower/all/nba")
    driver.maximize_window()
    time.sleep(3)
    email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.styles__field__Q6LKF [data-testid="email_input"]')))
    email_input.send_keys(username)
    password_input = driver.find_element(By.CSS_SELECTOR, '.styles__field__Q6LKF [data-testid="password_input"]')
    password_input.send_keys(password)
    sign_in_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="sign-in-button"]')
    sign_in_button.click()
    # wait until user is signed in to go to pick-em webpage
    signed_in_verifier_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.styles__link__C_eQ8.styles__active__UQzgQ')))
    driver.get("https://underdogfantasy.com/pick-em/higher-lower/pre-game/nhl")

def write_to_csv(data):
    current_date = datetime.now().strftime("%Y-%m-%d")
    csv_file_path = f'odds-lines-data/underdog-lines/nhl/nhl_underdog_lines_{current_date}.csv'
    directory = os.path.dirname(csv_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Extract all unique property names from data
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for player_data in data:
            writer.writerow(player_data)

def find_player_and_props(driver, player_prop_div):
    player_name_element = WebDriverWait(player_prop_div, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.styles__playerName__jW6mb')))
    player_name = player_name_element.text
    try:
        more_picks_button = WebDriverWait(player_prop_div, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button")))[-1]
        more_picks_span = more_picks_button.find_element(By.CSS_SELECTOR, 'span')
        if "More picks" in more_picks_span.text:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", more_picks_button)
            more_picks_button.click()
    except:
        None
    props = []
    stat_line_elements = player_prop_div.find_elements(By.CSS_SELECTOR, 'div.styles__overUnderListCell__tbRod')
    # Loop through each prop and extract the prop name and value
    for stat_line_element in stat_line_elements:
        prop = stat_line_element.find_element(By.CSS_SELECTOR, 'p').text
        value, prop_name = prop.split(' ', 1)  # Split by the first space
        prop_choice_div = stat_line_element.find_element(By.CSS_SELECTOR, 'div.styles__overUnderOptionsWrapper__EMqt9')
        betting_option_buttons = prop_choice_div.find_elements(By.CSS_SELECTOR, "button")
        has_lower_betting_option = False
        has_higher_betting_option = False
        multiplier = "1x"
        for button in betting_option_buttons:
            if "x" in button.text:
                multiplier = button.text.split("\n")[1]
            if "Lower" in button.text:
                has_lower_betting_option = True
            elif "Higher" in button.text:
                has_higher_betting_option = True
        if has_lower_betting_option and has_higher_betting_option:
            prop_choice = "C"
        if has_lower_betting_option and not has_higher_betting_option:
            prop_choice = "L"
        if not has_lower_betting_option and has_higher_betting_option:
            prop_choice = "H"
        # Check if prop is a scorcher
        has_scorcher_button = False
        try:
            i_elements = stat_line_element.find_elements(By.CSS_SELECTOR, 'i.styles__icon__DijND.styles__lineIcon__hL7Gn')
            if i_elements:
                has_scorcher_button = True
        except:
            None
        # print("prop_name:", prop_name, "prop_choice:", prop_choice, "multiplier:", multiplier, "value:", value, "has_scorcher_button:", has_scorcher_button)
        props.append({'prop': prop_name, 'prop_choice': prop_choice, "multiplier": multiplier, "value": value, 'has_scorcher_button': has_scorcher_button})
    
    return player_name, props

def scrape_nhl_lines():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    login(driver)
    player_prop_divs_containers = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.styles__content___R51k")))
    player_prop_divs = []

    for player_prop_divs_container in player_prop_divs_containers:
        current_player_prop_divs = player_prop_divs_container.find_elements(By.CSS_SELECTOR, "div.styles__overUnderCell__KgzNn")
        for player_prop_div in current_player_prop_divs:
            player_prop_divs.append(player_prop_div)

    data = []
    for player_prop_div in player_prop_divs:  # Loop through each player's full prop div
        player_name, props = find_player_and_props(driver, player_prop_div=player_prop_div)
        player_data = {'Name': player_name}
        for prop in props:
            prop_name = prop['prop']
            prop_choice = prop['prop_choice']
            value = prop['value']
            has_scorcher_button = prop['has_scorcher_button']
            if "Power" in prop_name:
                prop_name = "PowerPlayPoints"
            if "Fantasy" in prop_name:
                prop_name = "Fantasy"
            if "Goals" in prop_name:
                prop_name = "GoalsAgainst"
            if "Blocked" in prop_name:
                prop_name = "BlockedShots"
            # Change prop names to match CSV field name
            prop_name = prop_name + prop_choice
            if has_scorcher_button:
                value = value + "s"
            value = value + "x" + prop['multiplier'].replace("x", "")
            player_data[prop_name] = value
        data.append(player_data)
        # print(player_data)
    write_to_csv(data)
    driver.quit()

if __name__ == "__main__":
    scrape_nhl_lines()