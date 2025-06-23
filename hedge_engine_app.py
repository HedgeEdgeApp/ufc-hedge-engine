import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# Title
st.title("🧠 UFC Hedge Engine")

st.markdown("This tool helps you calculate hedge options based on your bet outcomes and the final fight of the night.")

# User Inputs
st.header("🔢 Input Your Bets and Final Fight")

# 📦 Dynamic Bets
st.subheader("🧾 Add Your Bets")

num_bets = st.number_input("How many bets?", min_value=1, max_value=10, value=1, step=1)
bets = []
final_bet_index = None

for i in range(num_bets):
    st.markdown(f"---")
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    st.markdown(f"#### {name}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    result = st.selectbox(f"✅ {name} – result?", options=["TBD", "Yes", "No"], key=f"result_{i}")
    is_subject_to_hedge = st.checkbox("☑️ This bet depends on the final outcome (subject to hedge)", key=f"hedge_{i}")
    is_final_bet = st.checkbox("🏁 Is this the final fight you want to hedge?", key=f"final_{i}")
    if is_final_bet:
        final_bet_index = i
    bets.append({'name': name, 'odds': odds, 'stake': stake, 'result': result, 'hedged': is_subject_to_hedge})

# Final Fight Details
hedge_fighter = ""
hedge_odds = 0.0

if final_bet_index is not None:
    st.subheader("💥 Final Fight Hedge Details")
    hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
    hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    for hedge in hedge_steps:
        total_stake = sum(bet['stake'] for bet in bets)
        hedge_return = hedge * hedge_odds
        total_wagered = total_stake + hedge

        bets_return_if_original = 0
        for bet in bets:
            if bet['result'] == "Yes":
                bets_return_if_original += bet['stake'] * bet['odds']
            elif bet['result'] == "TBD" and bet['hedged']:
                bets_return_if_original += bet['stake'] * bet['odds']

        profit_if_original = bets_return_if_original - total_wagered
        profit_if_hedge = hedge_return - total_wagered if all(
            bet['result'] == "No" or (bet['result'] == "TBD" and bet['hedged']) for bet in bets
        ) else hedge_return + sum(
            bet['stake'] * bet['odds'] for bet in bets if bet['result'] == "Yes" and not bet['hedged']
        ) - total_wagered

        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_wagered,
            "Return if Original Fighter Wins": round(bets_return_if_original, 2),
            "Profit if Original Fighter Wins": round(profit_if_original, 2),
            f"Return if {hedge_fighter} (Hedge) Wins": round(hedge_return, 2),
            f"Profit if {hedge_fighter} (Hedge) Wins": round(profit_if_hedge, 2),
        })

    df = pd.DataFrame(data)

    st.markdown("### ✅ Scenario Overview")
    scenario_summary = [
        f"{bet['name']} ✅" if bet['result'] == "Yes"
        else f"{bet['name']} ❌" if bet['result'] == "No"
        else f"{bet['name']} ❓" for bet in bets
    ]
    st.markdown("**Scenario:** " + " | ".join(scenario_summary))

    # Format currency
    df_display = df.copy()
    for col in df_display.columns:
        if "Return" in col or "Profit" in col or "Wagered" in col or "Hedge Stake" in col:
            df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}")

    # Use AgGrid for pinned first column
    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_column("Hedge Stake", pinned="left")
    gb.configure_grid_options(domLayout='normal')
    grid_options = gb.build()

    AgGrid(df_display, gridOptions=grid_options, height=400, theme="streamlit")
