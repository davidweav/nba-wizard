import requests
from datetime import datetime, time
import pytz
import json
import argparse

def fetch_nba_events(api_key):
    games = {}
    base_url = "https://api.the-odds-api.com/v4"
    sport = "basketball_nba"  # Adjust the sport based on the desired basketball league
    regions = "us"
    url = f"{base_url}/sports/{sport}/odds/?apiKey={api_key}&regions={regions}"
    # print(url)
    response = requests.get(url)
    if response.status_code == 401: # this api key is out of uses
        print("Request quoata has been reached for", api_key)
        return False
    events_data = response.json()
    eastern_timezone = pytz.timezone("US/Eastern")
    try:
        for idx, event in enumerate(events_data):
            event_id = event.get("id")
            commence_time_str = event.get("commence_time")
            teams = (event.get("home_team"), event.get("away_team"))

            if event_id and commence_time_str and teams:
                commence_datetime = datetime.fromisoformat(commence_time_str.replace("Z", "+00:00"))
                print("Commence Time:", commence_datetime)
                commence_datetime_et = commence_datetime.astimezone(eastern_timezone)
                print("Commence Time ET:", commence_datetime_et)
                current_datetime_et = datetime.now(eastern_timezone)
                print("Current datetime et:", current_datetime_et)
                nine_pm_today = datetime.now(eastern_timezone).replace(hour=21, minute=0, second=0, microsecond=0)
                print("9pm datetime:",nine_pm_today)
                var = current_datetime_et > nine_pm_today
                print("Current time > 9pm:", var)
                var2 = commence_datetime_et.time() > current_datetime_et.time()
                print("Commence time > current time", var2, commence_datetime_et.time(), current_datetime_et.time())
                var3 = commence_datetime_et.date() == current_datetime_et.date()
                print("Commence time date == current time date:", var3, commence_datetime_et.date(), current_datetime_et.date())
                if (current_datetime_et > nine_pm_today) or (commence_datetime_et.time() > current_datetime_et.time() and commence_datetime_et.date() == current_datetime_et.date()):
                    formatted_date = commence_datetime_et.strftime("%Y-%m-%d")
                    formatted_time = commence_datetime_et.strftime("%H:%M:%S")

                    games[idx] = {
                        "event_id": event_id,
                        "date": formatted_date,
                        "time": formatted_time,
                        "teams": teams
                    }

        current_date = datetime.now().strftime("%Y-%m-%d")
        with open(f"betonline_scripts/events/nba_games_{current_date}.json", "w") as json_file:
            json.dump(games, json_file, indent=2)

        return True
    except Exception as e:
        return False
