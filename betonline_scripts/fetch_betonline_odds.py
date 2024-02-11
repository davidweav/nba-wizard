from betonline_scripts import get_nba_events as nbaE
from betonline_scripts import get_nba_pp as nbaPP

def get_betonline_odds():
    api_keys = ["a66b087a4628fe473a0d84cc8dd14533", "162e2c909f97655391e7fd98fcbaffdb", "c8e95f0047d9742ffbc3b8680892779c",
            "36aab4f1365caf620725f785b70db26a", "babd3fe7586d4ad29d3a4dabb0c74619", "35b4f6c81244ad6f6d5fcb31a2ed6186",
            "f38ade5fae57cb4dc717f360278feb51", "8c555e4dc5549b0e71792d8fa20e7761", "be937dc4ffa9e2ae7e65a31011706286",
            "6c2348d0288b716be3c9d7e61ecff61b", "397f04f9381b61210c5072ca73f40353", "64bd4f8b7caca019178a1dd8b0c44d4c"]
    current_api_key = None
    for api_key in api_keys:
        if nbaE.fetch_nba_events(api_key):
            current_api_key = api_key
            break
    print(current_api_key)

    for api_key in api_keys[api_keys.index(current_api_key):]:
        val = nbaPP.fetch_nba_pp(api_key)
        if val:
            current_api_key = api_key
            break
