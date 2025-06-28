import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sports Betting Hedge Engine", layout="wide")

# Display banner image (optional)
st.image("hedge_edge_banner.png", use_container_width=True)

st.markdown("---")

# Store all bets
bets = []

# Number of bets
num_bets = st.number_input("How many bets do you want to enter?", min_value=1, step=1, value=1)

# Collect each bet's data (stacked layout)
for i in range(num_bets):
    st.markdown(f"### \U0001F9FE Bet #{i+1}")
    name = st.text_input(f"Bet #{i+1} Name", key=f"name_{i}")
    odds = st.number_input("Odds", min_value=1.0, step=0.01, key=f"odds_{i}")
    stake = st.number_input("Stake ($)", min_value=0.0, step=1.0, key=f"stake_{i}")
    result = st.selectbox("Did it win?", ["TBD", "Yes", "No"], key=f"result_{i}")
    subject_to_hedge = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_dependent_{i}")
    hedge_side_exposure = st.checkbox("This bet includes the hedge fighter (hedge side exposure)", key=f"hedge_side_{i}")

    bets.append({
        "name": name,
        "odds": odds,
        "stake": stake,
        "result": result,
        "subject_to_hedge": subject_to_hedge,
        "hedge_side_exposure": hedge_side_exposure
    })

# Final Event Details
st.markdown("### \U0001F4A3 Final Event Details")
col1, col2 = st.columns(2)
fighter_a = col1.text_input("Fighter A (Original Side)", key="fighter_a")
fighter_b = col2.text_input("Fighter B (Hedge Side)", key="fighter_b")

hedge_fighter = fighter_b
hedge_odds = st.number_input("Odds for the hedge event", min_value=1.0, step=0.01)

# Hedge Stake Unit Selector
hedge_unit = st.number_input("Hedge Stake Unit ($)", min_value=1, step=1, value=10)
max_hedge = st.number_input("Maximum Hedge Stake ($)", min_value=hedge_unit, step=hedge_unit, value=300)

# Hedge matrix generation
rows = []

for hedge_stake in range(0, max_hedge + 1, hedge_unit):
    total_staked = sum(bet["stake"] for bet in bets) + hedge_stake

    # Return if Fighter A Wins: include all bets marked Yes or TBD that are NOT hedge side exposure
    fighter_a_returns = sum(
        bet["stake"] * bet["odds"]
        for bet in bets
        if bet["result"] in ["Yes", "TBD"] and not bet["hedge_side_exposure"]
    )

    # Return if Fighter B Wins: include all bets marked Yes or TBD that ARE hedge side exposure
    fighter_b_returns = sum(
        bet["stake"] * bet["odds"]
        for bet in bets
        if bet["result"] in ["Yes", "TBD"] and bet["hedge_side_exposure"]
    )

    hedge_return = hedge_stake * hedge_odds
    profit_if_a = fighter_a_returns - total_staked
    profit_if_b = hedge_return + fighter_b_returns - total_staked

    rows.append({
        "Hedge Stake": f"${hedge_stake:.2f}",
        "Total Wagered": f"${total_staked:.2f}",
        f"Return if {fighter_a} (Original) Wins": f"${fighter_a_returns:.2f}",
        f"Profit if {fighter_a} (Original) Wins": f"${profit_if_a:.2f}",
        f"Return if {fighter_b} (Hedge) Wins": f"${hedge_return + fighter_b_returns:.2f}",
        f"Profit if {fighter_b} (Hedge) Wins": f"${profit_if_b:.2f}"
    })

df = pd.DataFrame(rows)

# Scenario Summary
scenario_parts = []
for bet in bets:
    emoji = "❓" if bet["result"] == "TBD" else "✅" if bet["result"] == "Yes" else "❌"
    scenario_parts.append(f"{bet['name']} {emoji}")

st.markdown("### \U0001F4A5 Scenario Summary")
st.markdown(f"**Scenario:** {' / '.join(scenario_parts)}")

# Show hedge matrix
st.dataframe(df, hide_index=True, use_container_width=True)

# Clarifying message for user context
if fighter_a and fighter_b:
    st.info(f"\U0001F4AC You are currently hedging on **{fighter_b}**. All other returns are attributed to **{fighter_a} (Original Side)**.")
