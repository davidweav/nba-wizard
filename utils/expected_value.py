def calculate_expected_value(prob_win_list, multiplier_list, payout_multiplier, bet):
    # EV = P(win) x Payout - P(loss) x Bet
    prob_win_combined = 1
    for prob in prob_win_list:
        prob_win_combined *= prob
    prob_lose = 1 - prob_win_combined
    
    expected_payout = payout_multiplier
    for multiplier in multiplier_list:
        expected_payout *= multiplier
    
    ev = prob_win_combined * expected_payout * bet - prob_lose * bet
    return ev


prob_win_list = [0.7297, .7183]
multiplier_list = [.7, .7]
payout_multiplier = 3
bet = 5

ev = calculate_expected_value(prob_win_list, multiplier_list, payout_multiplier, bet)
# Expected value means the average amount of money you can expect to win or lose if 
# you place the same bet on the same odds multiple times. How many times you need to
# 
print("Expected value:", ev)
        