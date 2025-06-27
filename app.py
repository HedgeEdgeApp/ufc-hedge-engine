import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sports Betting Hedge Engine", layout="wide")

# 🔧 Full-width banner container
with st.container():
    st.markdown("""
        <div style='
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #111827;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 10px;
        '>
            <img src='hedge_edge_banner.png' style='width: 100%; max-width: 1000px; height: auto;'>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 💰 Stake Unit Selection
hedge_unit = st.number_input("Hedge Stake Unit ($)", min_value=1.0, step=1.0, value=10.0)
max_hedge = st.number_input("Max Hedge Stake ($)", min_value=hedge_unit, step=hedge_unit, value=300.0)

# 🧾 Store all bets
bets = []

num_bets = st.number_input("How many bets do you want to enter?", min_value=1, step=1, value=1)

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

# 🔥 Final Fight Details
st.markdown("### 💥 Final Fight Details")
hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
hedge_odds = st.number_input("Odds for hedge fighter", min_value=1.0, step=0.01)

# 🧮 Hedge Table Generation
rows = []
hedge_stakes = [x for x in range(0, int(max_hedge + hedge_unit), int(hedge_unit))]

for hedge_stake in hedge_stakes:
    total_staked = sum(bet["stake"] for bet in bets) + hedge_stake

    original_returns = 0
    for bet in bets:
        if bet["result"] == "Yes":
            original_returns += bet["stake"] * bet["odds"]
        elif bet["result"] == "TBD" and not bet["subject_to_hedge"]:
            original_returns += bet["stake"] * bet["odds"]
        elif bet["result"] == "TBD" and bet["subject_to_hedge"]:
            original_returns += bet["stake"] * bet["odds"]

    hedge_return = hedge_stake * hedge_odds

    rows.append({
        "Hedge Stake": f"${hedge_stake:.2f}",
        "Total Wagered": f"${total_staked:.2f}",
        "Return if Original Wins": f"${original_returns:.2f}",
        "Profit if Original Wins": f"${original_returns - total_staked:.2f}",
        f"Return if {hedge_fighter} (Hedge) Wins": f"${hedge_return:.2f}",
        f"Profit if {hedge_fighter} (Hedge) Wins": f"${hedge_return - total_staked:.2f}",
    })

df = pd.DataFrame(rows)

# 📋 Scenario Summary
scenario_parts = []
for bet in bets:
    emoji = "❓" if bet["result"] == "TBD" else "✅" if bet["result"] == "Yes" else "❌"
    scenario_parts.append(f"{bet['name']} {emoji}")

st.markdown("### 📋 Scenario Summary")
st.markdown(f"**Scenario:** {' / '.join(scenario_parts)}")

# 📊 Display Table
st.dataframe(df, hide_index=True, use_container_width=True)
