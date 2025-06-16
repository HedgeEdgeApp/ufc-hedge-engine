import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Hedge Engine", layout="centered")
st.title("UFC Hedge Engine")
st.markdown("""
Upload your parlay bet data and get auto-generated hedge scenarios for the final fight.
Start simple and we can build layers of complexity later.
""")

# Input section
st.header("Enter Parlay Bets")
num_parlays = st.number_input("How many parlays?", min_value=1, max_value=10, value=2)

parlays = []
for i in range(num_parlays):
    st.subheader(f"Parlay #{i+1}")
    fighters = st.text_input(f"Fighters in Parlay #{i+1} (comma separated)", key=f"fighters_{i}")
    stake = st.number_input(f"Stake for Parlay #{i+1} ($)", key=f"stake_{i}")
    odds = st.number_input(f"Odds for Parlay #{i+1} (decimal)", min_value=1.01, step=0.01, key=f"odds_{i}")
    parlays.append({"fighters": [f.strip() for f in fighters.split(",")], "stake": stake, "odds": odds})

# Final fight info
st.header("Final Fight Info")
final_fight_fighter_a = st.text_input("Final Fight - Fighter A (your pick)")
final_fight_fighter_b = st.text_input("Final Fight - Fighter B")
odds_b = st.number_input(f"Odds for {final_fight_fighter_b} to win (decimal)", min_value=1.01, step=0.01)

# Show hedge outcomes
def calculate_hedge(parlays, final_pick, hedge_pick, hedge_odds):
    results = []
    for p in parlays:
        active = final_pick in p["fighters"] or hedge_pick in p["fighters"]
        won = final_pick in p["fighters"]
        stake = p["stake"]
        odds = p["odds"]

        if won:
            profit_win = stake * odds
        else:
            profit_win = 0

        if hedge_pick in p["fighters"]:
            profit_lose = stake * odds
        else:
            profit_lose = 0

        results.append({
            "Parlay": p["fighters"],
            "Stake": stake,
            "Return if A Wins": round(profit_win, 2),
            "Return if B Wins": round(profit_lose, 2),
            "Profit if A Wins": round(profit_win - stake, 2),
            "Profit if B Wins": round(profit_lose - stake, 2),
        })
    return results

if st.button("Run Hedge Simulation"):
    table = calculate_hedge(parlays, final_fight_fighter_a, final_fight_fighter_b, odds_b)
    st.write("### Hedge Outcome Table")
    df = pd.DataFrame(table)
    st.dataframe(df)
    
    # Totals
    total_stake = sum(p["stake"] for p in parlays)
    total_return_a = sum(row["Return if A Wins"] for row in table)
    total_return_b = sum(row["Return if B Wins"] for row in table)
    st.markdown(f"**Total Wagered:** ${total_stake:.2f}")
    st.markdown(f"**Total Return if {final_fight_fighter_a} Wins:** ${total_return_a:.2f} | Profit: ${total_return_a - total_stake:.2f}")
    st.markdown(f"**Total Return if {final_fight_fighter_b} Wins:** ${total_return_b:.2f} | Profit: ${total_return_b - total_stake:.2f}")
