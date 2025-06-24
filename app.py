import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Hedge Engine", layout="wide")
st.title("🤼 UFC Hedge Engine")
st.markdown("---")

# Store all bets
bets = []

# Number of bets
num_bets = st.number_input("How many bets do you want to enter?", min_value=1, step=1, value=1)

# Collect each bet's data (stacked layout)
for i in range(num_bets):
    st.markdown(f"### 🧾 Bet #{i+1}")
    name = st.text_input(f"Bet #{i+1} Name", key=f"name_{i}")
    odds = st.number_input("Odds", min_value=1.0, step=0.01, key=f"odds_{i}")
    stake = st.number_input("Stake ($)", min_value=0.0, step=1.0, key=f"stake_{i}")
    result = st.selectbox("Did it win?", ["TBD", "Yes", "No"], key=f"result_{i}")
    subject_to_hedge = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_dependent_{i}")

    bets.append({
        "name": name,
        "odds": odds,
        "stake": stake,
        "result": result,
        "subject_to_hedge": subject_to_hedge
    })

# Final fight hedge details
st.markdown("### 💥 Final Fight Details")
hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
hedge_odds = st.number_input("Odds for hedge fighter", min_value=1.0, step=0.01)

# NEW: Hedge Stake Configuration
st.markdown("### ⚙️ Hedge Settings")
hedge_unit = st.number_input("Hedge Stake Unit ($)", min_value=0.01, step=0.01, value=10.00)
max_hedge = st.number_input("Maximum Hedge Stake ($)", min_value=hedge_unit, step=hedge_unit, value=300.00)

# Hedge matrix generation
def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

rows = []

for hedge_stake in frange(0, max_hedge, hedge_unit):
    total_staked = sum(bet["stake"] for bet in bets) + hedge_stake

    # Original fighter outcome
    original_returns = 0
    for bet in bets:
        if bet["result"] == "Yes":
            original_returns += bet["stake"] * bet["odds"]
        elif bet["result"] == "TBD" and not bet["subject_to_hedge"]:
            original_returns += bet["stake"] * bet["odds"]

    profit_if_original = original_returns - total_staked

    # Hedge outcome
    hedge_return = hedge_stake * hedge_odds
    profit_if_hedge = hedge_return - total_staked

    rows.append({
        "Hedge Stake": f"${hedge_stake:.2f}",
        "Total Wagered": f"${total_staked:.2f}",
        "Return if Original Wins": f"${original_returns:.2f}",
        "Profit if Original Wins": f"${profit_if_original:.2f}",
        f"Return if {hedge_fighter} (Hedge) Wins": f"${hedge_return:.2f}",
        f"Profit if {hedge_fighter} (Hedge) Wins": f"${profit_if_hedge:.2f}",
    })

df = pd.DataFrame(rows)

# Emoji summary (goes ABOVE the table)
scenario_parts = []
for bet in bets:
    emoji = "❓" if bet["result"] == "TBD" else "✅" if bet["result"] == "Yes" else "❌"
    scenario_parts.append(f"{bet['name']} {emoji}")
st.markdown("### 📋 Scenario Summary")
st.markdown(f"**Scenario:** {' / '.join(scenario_parts)}")

# Show final hedge matrix table
st.dataframe(df, hide_index=True, use_container_width=True)
