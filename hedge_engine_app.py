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
    st.markdown(f"---")  # divider first
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    st.markdown(f"#### {name}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    won = st.selectbox(f"✅ {name} – win?", options=["TBD", "Yes", "No"], key=f"result_{i}")
    is_final_fight = st.checkbox("🔚 This bet depends on the final outcome (subject to hedge)", key=f"hedge_{i}")
    bets.append({
        'name': name,
        'odds': odds,
        'stake': stake,
        'won': won,
        'is_final_fight': is_final_fight
    })

# 💥 Final Fight Details
st.subheader("💥 Final Fight Details")
hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# Optional Original Fighter field (for table labeling, polishing later)
# original_fighter = st.text_input("Original Fighter (optional label)", value="Rountree")

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

        # If original bets win (hedge loses)
        bets_return = sum(
            bet['stake'] * bet['odds']
            for bet in bets
            if bet['won'] == "Yes" or (bet['won'] == "TBD" and bet['is_final_fight'])
        )
        profit_bets_win = bets_return - total_staked

        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_staked,
            "Return if Original Fighter Wins": round(bets_return, 2),
            "Profit if Original Fighter Wins": round(profit_bets_win, 2),
            f"Return if {hedge_fighter} (Hedge) Wins": round(hedge_return, 2),
            f"Profit if {hedge_fighter} (Hedge) Wins": round(profit_hedge_win, 2),
        })

    df = pd.DataFrame(data)

    # 💡 Format currency
    display_df = df.copy()
    for col in display_df.columns:
        if "Return" in col or "Profit" in col or "Wagered" in col or "Hedge Stake" in col:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")

    st.markdown("### Scenario Summary")
    scenario_summary = []
    for bet in bets:
        if bet['won'] == "TBD" and bet['is_final_fight']:
            icon = "❓"
        elif bet['won'] == "Yes":
            icon = "✅"
        elif bet['won'] == "No":
            icon = "❌"
        else:
            icon = ""
        scenario_summary.append(f"{bet['name']} {icon}")
    st.markdown(" | ".join(scenario_summary))

    # 🧲 Display AgGrid table with first column frozen
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_column("Hedge Stake", pinned="left")
    grid_options = gb.build()

    st.markdown("### 📊 Hedge Matrix")
    AgGrid(display_df, gridOptions=grid_options, height=500, fit_columns_on_grid_load=True)  
