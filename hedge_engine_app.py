import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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
    st.markdown(f"---")
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    st.markdown(f"#### {name}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    won = st.selectbox(f"✅ {name} – win?", options=["TBD", "Yes", "No"], key=f"result_{i}")
    is_final = st.checkbox(f"📍 This bet depends on the final outcome (subject to hedge)?", key=f"final_{i}")
    bets.append({'name': name, 'odds': odds, 'stake': stake, 'won': won, 'final': is_final})

# 💥 Final Fight Details
st.subheader("💥 Final Fight Details")

hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)", value="Smith")
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# 🧮 Run the Calculation
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    # Summary display above table
    scenario_summary = []
    for bet in bets:
        if bet['final']:
            scenario_summary.append(f"{bet['name']} ❓")
        elif bet['won'] == "Yes":
            scenario_summary.append(f"{bet['name']} ✅")
        elif bet['won'] == "No":
            scenario_summary.append(f"{bet['name']} ❌")
        else:
            scenario_summary.append(f"{bet['name']} ❓")

    st.markdown(f"**Scenario:** {' | '.join(scenario_summary)}")

    for hedge in hedge_steps:
        confirmed_bets = [b for b in bets if not b['final'] and b['won'] == "Yes"]
        final_fight_bets = [b for b in bets if b['final']]

        total_bets_stake = sum(b['stake'] for b in bets)
        total_staked = total_bets_stake + hedge

        original_return = sum(b['stake'] * b['odds'] for b in confirmed_bets) + \
                          sum(b['stake'] * b['odds'] for b in final_fight_bets)
        profit_original = original_return - total_staked

        hedge_return = hedge * hedge_odds
        profit_hedge = hedge_return + sum(b['stake'] * b['odds'] for b in confirmed_bets) - total_staked

        data.append({
            "Hedge Stake ($)": hedge,
            "Total Wagered": round(total_staked, 2),
            "Return if Original Fighter Wins": round(original_return, 2),
            "Profit if Original Fighter Wins": round(profit_original, 2),
            f"Return if {hedge_fighter} (Hedge) Wins": round(hedge_return + sum(b['stake'] * b['odds'] for b in confirmed_bets), 2),
            f"Profit if {hedge_fighter} (Hedge) Wins": round(profit_hedge, 2),
        })

    df = pd.DataFrame(data).reset_index(drop=True)  # ← IMPORTANT: remove the default index

    # 🧲 AgGrid with sticky "Hedge Stake ($)" as the new first column
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("Hedge Stake ($)", pinned="left")
    gb.configure_default_column(resizable=True, filter=True, sortable=True)
    grid_options = gb.build()

    st.markdown("### 💡 Hedge Matrix")
    AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.NO_UPDATE,
        allow_unsafe_jscode=True,
        height=400, 
        fit_columns_on_grid_load=True,
    )
