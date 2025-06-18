import streamlit as st
import pandas as pd

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
    won = st.selectbox(f"✅ {name} – win?", options=["Yes", "No"], key=f"result_{i}")
    bets.append({'name': name, 'odds': odds, 'stake': stake, 'won': won})

# 💥 Final Fight Details
st.subheader("💥 Final Fight Details")
hedge_fighter = st.text_input("Hedge (Fighter Name)", value="Smith")
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# Run calc
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    col_return_hedge = f"Return if {hedge_fighter} Wins"
    col_profit_hedge = f"Profit if {hedge_fighter} Wins"

    for hedge in hedge_steps:
        total_bets_stake = sum(bet['stake'] for bet in bets)
        total_staked = total_bets_stake + hedge

        hedge_return = hedge * hedge_odds
        profit_hedge_win = hedge_return - total_staked

        bets_return = sum(bet['stake'] * bet['odds'] for bet in bets if bet['won'] == "Yes")
        profit_bets_win = bets_return - total_staked

        row = {
            "Hedge Stake": hedge,
            "Total Wagered": total_staked,
            "Return if Winning Bets Hit": round(bets_return, 2),
            "Profit if Winning Bets Hit": round(profit_bets_win, 2),
            col_return_hedge: round(hedge_return, 2),
            col_profit_hedge: round(profit_hedge_win, 2),
        }
        data.append(row)

    # Set column order explicitly
    column_order = [
        "Hedge Stake",
        "Total Wagered",
        "Return if Winning Bets Hit",
        "Profit if Winning Bets Hit",
        col_return_hedge,
        col_profit_hedge,
    ]

    df = pd.DataFrame(data, columns=column_order)

    # Format currency
    df_display = df.copy()
    for col in df.columns:
        if (
            "Return" in col
            or "Profit" in col
            or "Wagered" in col
            or "Hedge Stake" in col
        ):
            df_display[col] = df[col].apply(lambda x: f"${x:,.2f}")

    st.success("✅ Hedge Matrix Generated:")
    st.dataframe(df_display)

    # Scenario summary
    scenario_summary = [f"{bet['name']} {'✅' if bet['won'] == 'Yes' else '❌'}" for bet in bets]
    if scenario_summary:
        st.markdown(f"**Scenario:** {' | '.join(scenario_summary)}") 
