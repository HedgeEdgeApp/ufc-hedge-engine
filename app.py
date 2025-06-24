import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Hedge Engine", layout="wide")
st.title("🤼 UFC Hedge Engine")
st.markdown("---")

# Store all bets
bets = []

# Number of bets
num_bets = st.number_input("How many bets do you want to enter?", min_value=1, step=1, value=1)

# Collect each bet's data
for i in range(num_bets):
    st.markdown(f"### 🧾 Bet #{i+1}")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        name = st.text_input(f"Bet #{i+1} Name", key=f"name_{i}")
    with col2:
        odds = st.number_input(f"Odds", min_value=1.0, step=0.01, key=f"odds_{i}")
    with col3:
        stake = st.number_input(f"Stake ($)", min_value=0.0, step=1.0, key=f"stake_{i}")
    with col4:
        result = st.selectbox("Did it win?", ["TBD", "Yes", "No"], key=f"result_{i}")
    with col5:
        subject_to_hedge = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_dependent_{i}")
    
    bets.append({
        "name": name,
        "odds": odds,
        "stake": stake,
        "result": result,
        "subject_to_hedge": subject_to_hedge
    })

# Final fight details
st.markdown("### 💥 Final Fight Details")
final_fight_col1, final_fight_col2 = st.columns(2)
with final_fight_col1:
    hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)", key="hedge_fighter")
with final_fight_col2:
    hedge_odds = st.number_input("Odds for hedge fighter", min_value=1.0, step=0.01, key="hedge_odds")

# Calculate outcomes
max_hedge = 300
rows = []

for hedge_stake in range(0, max_hedge + 1, 10):
    total_staked = sum(bet['stake'] for bet in bets) + hedge_stake

    # Determine if original fighter wins
    original_returns = 0
    for bet in bets:
        if bet['result'] == "Yes":
            original_returns += bet['odds'] * bet['stake']
        elif bet['result'] == "TBD" and not bet['subject_to_hedge']:
            original_returns += bet['odds'] * bet['stake']
    profit_if_original = original_returns - total_staked

    # Hedge outcome
    return_if_hedge = hedge_stake * hedge_odds
    profit_if_hedge = return_if_hedge - total_staked

    rows.append({
        "Hedge Stake": f"${hedge_stake:.2f}",
        "Total Wagered": f"${total_staked:.2f}",
        "Return if Original Wins": f"${original_returns:.2f}",
        "Profit if Original Wins": f"${profit_if_original:.2f}",
        f"Return if {hedge_fighter} (Hedge) Wins": f"${return_if_hedge:.2f}",
        f"Profit if {hedge_fighter} (Hedge) Wins": f"${profit_if_hedge:.2f}"
    })

df = pd.DataFrame(rows)

# Emoji Scenario Display
scenario_parts = []
for bet in bets:
    emoji = "❓" if bet['result'] == "TBD" else "✅" if bet['result'] == "Yes" else "❌"
    scenario_parts.append(f"{bet['name']} {emoji}")
st.markdown(f"**Scenario:** {' / '.join(scenario_parts)}")

# Show result table
st.dataframe(df, hide_index=True, use_container_width=True)
