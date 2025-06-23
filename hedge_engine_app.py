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

for i in range(num_bets):
    st.markdown("---")
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    st.markdown(f"#### {name}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    won = st.selectbox(f"✅ {name} – win?", options=["TBD", "Yes", "No"], key=f"result_{i}")
    subject_to_hedge = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_{i}")
    bets.append({'name': name, 'odds': odds, 'stake': stake, 'won': won, 'hedged': subject_to_hedge})

# 💥 Final Fight Details
st.subheader("💥 Final Fight Details")
hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)", value="Smith")
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# Run calc
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    for hedge in hedge_steps:
        total_bets_stake = sum(b['stake'] for b in bets)
        total_staked = total_bets_stake + hedge

        # Only count bets not marked TBD
        bets_return = sum(
            b['stake'] * b['odds'] for b in bets
            if b['won'] == "Yes" or (b['won'] == "TBD" and not b['hedged'])
        )

        # If hedge hits (final fight wins), then all bets marked 'hedged' are assumed to have lost
        # Only return from non-hedged wins
        hedge_wins = all(
            b['won'] != "Yes" if b['hedged'] else True for b in bets
        )
        hedge_return = hedge * hedge_odds if hedge_wins else 0

        # Determine if original (non-hedged bets) return money
        hedged_loss = any(b['hedged'] and b['won'] == "No" for b in bets)
        profit_hedge_win = hedge_return - total_staked
        profit_bets_win = bets_return - total_staked

        data.append({
            "Hedge Stake ($)": hedge,
            "Total Wagered": total_staked,
            "Return if Original Fighter Wins": round(bets_return, 2),
            "Profit if Original Fighter Wins": round(profit_bets_win, 2),
            f"Return if {hedge_fighter} (Hedge) Wins": round(hedge_return, 2),
            f"Profit if {hedge_fighter} (Hedge) Wins": round(profit_hedge_win, 2),
        })

    df = pd.DataFrame(data)

    # 🔒 Pin hedge stake column
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("Hedge Stake ($)", pinned="left")
    grid_options = gb.build()

    st.success("✅ Hedge Matrix Generated:")
    AgGrid(df, gridOptions=grid_options, height=500, fit_columns_on_grid_load=True)

    # Scenario summary
    scenario_summary = []
    for b in bets:
        if b['won'] == "TBD" and b['hedged']:
            scenario_summary.append(f"{b['name']} ❓")
        else:
            scenario_summary.append(f"{b['name']} {'✅' if b['won']=='Yes' else '❌'}")
    if scenario_summary:
        st.markdown(f"**Scenario:** {' | '.join(scenario_summary)}") 
