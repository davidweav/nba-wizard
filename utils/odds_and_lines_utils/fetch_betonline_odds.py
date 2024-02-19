from utils.odds_and_lines_utils.oddsAPI_utils import fetch_nba_odds_and_lines, fetch_nhl_odds_and_lines

api_keys = ["a66b087a4628fe473a0d84cc8dd14533", "162e2c909f97655391e7fd98fcbaffdb", "c8e95f0047d9742ffbc3b8680892779c",
            "36aab4f1365caf620725f785b70db26a", "babd3fe7586d4ad29d3a4dabb0c74619", "35b4f6c81244ad6f6d5fcb31a2ed6186",
            "f38ade5fae57cb4dc717f360278feb51", "8c555e4dc5549b0e71792d8fa20e7761", "be937dc4ffa9e2ae7e65a31011706286",
            "6c2348d0288b716be3c9d7e61ecff61b", "397f04f9381b61210c5072ca73f40353", "64bd4f8b7caca019178a1dd8b0c44d4c",
            "a9b0892d4fa2c57d57f1b05d67528e9a", "78a017c97a7acd60de2aec61bdd85513", "b57f760438ce24bae7dc8f53eb00eac3",
            "d82a67bc040548efeee3af1526c6a3de", "dc3c3fdb76f1bf7d13fe57e191b60c3c", "95b0a6d09132749036cfcc483babec56",
            "192de6d07fed5036cf4cb13a4d9cd7e0", "867b7e8685d483aa1c2aa01344a0400c", "0efc0f5d30144bbe626b8b3f467b8175",
            "50c1053c23a0e7d87290b7b2b457fb9f", "f1cb6fb98e427ee2c0063af5b2b346f4", "4c8208cf8c87e10ca3964b7cd0b957d3",
            "667c67acb59bbf7d815a229385d4f726", "70a414679d013fd8adf10521cebd83f0", "3d613dd69dbcb6a353c3fd0a71164f34",
            "143828b09a67e603da267a3bb7451680", "96cb7f8d4d687d1150a9909f2afbe383", "2f8ec3f56edf16c969345d485a2e7b6b",
            "45da45ad521c53974c1ac4eca5066fae", "846c38dd50fb01c78db0f00f0cc83f39", "3520471a8e8d578249b149f8bb7c95b8"]

def get_nba_betonline_odds():
    current_api_key = None
    for api_key in api_keys:
        if fetch_nba_odds_and_lines(api_key):
            current_api_key = api_key
            break
    print(current_api_key)

def get_nhl_betonline_odds():
    current_api_key = None
    for api_key in api_keys:
        if fetch_nhl_odds_and_lines(api_key):
            current_api_key = api_key
            break
    print(current_api_key)