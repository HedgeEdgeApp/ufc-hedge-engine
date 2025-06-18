import streamlit as st
import pandas as pd

# Title
st.title("🧠 UFC Hedge Engine")

st.markdown("This tool helps you calculate hedge options based on your bet outcomes and the final fight of the night.")

# User Inputs
st.header("🔢 Input Your Bets and Final Fight")

# Bet 1
# 📦 Dynamic Bets
st.subheader("🧾 Add Your Bets")

num_bets = st.number_input("How many bets?", min_value=1, max_value=10, value=1, step=1)
bets = []

for i in range(num_bets):
    st.markdown(f"---\n#### Bet #{i+1}")
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    won = st.selectbox(f"✅ {name} – win?", options=["Yes", "No"], key=f"result_{i}")
    bets.append({'name': name, 'odds': odds, 'stake': stake, 'won': won})


# Cleaner labels like "Smith – win?" or "Walker/Smith/Jones – win?"
def format_result_prompt(bet_name):
    return f"✅ {bet_name} – win?"

bet1_legs_hit = st.selectbox(format_result_prompt(bet1_name), options=["Yes", "No"])
bet2_legs_hit = st.selectbox(format_result_prompt(bet2_name), options=["Yes", "No"])

# Run calc
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    for hedge in hedge_steps:
    total_bets_stake = sum(bet['stake'] for bet in bets)
    total_staked = total_bets_stake + hedge

    # If hedge hits (bets lose)
    hedge_return = hedge * hedge_odds
    profit_hedge_win = hedge_return - total_staked

    # If bets win (hedge loses)
    bets_return = sum(bet['stake'] * bet['odds'] for bet in bets if bet['won'] == "Yes")
    profit_bets_win = bets_return - total_staked
        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_staked,
            f"Return if {hedge_fighter} Wins": round(hedge_return, 2),
            f"Profit if {hedge_fighter} Wins": round(profit_hedge_win, 2),
            "Return if Winning Bets Hit": round(bets_return, 2),
            "Profit if Winning Bets Hit": round(profit_bets_win, 2),
        })

    df = pd.DataFrame(data)
    st.success("✅ Hedge Matrix Generated:")
    df_display = df.copy()
    for col in df.columns:
        if "Return" in col or "Profit" in col or "Wagered" in col:
            df_display[col] = df[col].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_display)

    # Display selected bet outcomes below the table
    
    scenario_summary = [f"{bet['name']} {'✅' if bet['won'] == 'Yes' else '❌'}" for bet in bets]

    if scenario_summary:
        st.markdown(f"**Scenario:** {' | '.join(scenario_summary)}")
