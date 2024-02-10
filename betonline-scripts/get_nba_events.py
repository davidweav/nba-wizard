import requests
from datetime import datetime
import pytz
import json
import argparse

def fetch_nba_events(api_key):
    base_url = "https://api.the-odds-api.com/v4"
    sport = "basketball_nba"  # Adjust the sport based on the desired basketball league
    regions = "us"

    url = f"{base_url}/sports/{sport}/odds/?apiKey={api_key}&regions={regions}"
    # print(url)

    response = requests.get(url)
    if response.status_code == 401:
        print("Request quoata has been reached for", api_key)
        return False
    events_data = response.json()
    games_dictionary = {}
    eastern_timezone = pytz.timezone("US/Eastern")
    print("HELLO")
    try:
        current_time_utc = datetime.now(pytz.utc)
        for idx, event in enumerate(events_data):
            event_id = event.get("id")
            commence_time_str = event.get("commence_time")
            teams = (event.get("home_team"), event.get("away_team"))

            if event_id and commence_time_str and teams:
                commence_datetime = datetime.fromisoformat(commence_time_str.replace("Z", "+00:00"))
                
                # Convert to Eastern Time
                commence_datetime_et = commence_datetime.astimezone(eastern_timezone)

                print(commence_datetime_et.date(), current_date)
                if commence_datetime_et > current_time_utc and commence_datetime_et.date() == current_date:
                    formatted_date = commence_datetime_et.strftime("%Y-%m-%d")
                    formatted_time = commence_datetime_et.strftime("%H:%M:%S")

                    games_dictionary[idx] = {
                        "event_id": event_id,
                        "date": formatted_date,
                        "time": formatted_time,
                        "teams": teams
                    }

        current_date = datetime.now().strftime("%Y-%m-%d")
        with open(f"events/nba_games_{current_date}.json", "w") as json_file:
            json.dump(games_dictionary, json_file, indent=2)

        return True
    except Exception as e:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", help="Your API key for The Odds API")
    args = parser.parse_args()

    if args.api_key:
        fetch_nba_events(args.api_key)
    else:
        print("Please provide your API key using the --api_key argument.")