import streamlit as st
import pandas as pd

# Title
st.title("🧠 UFC Hedge Engine")

st.markdown("This tool helps you calculate hedge options based on your parlay outcomes and the final fight of the night.")

# User Inputs
st.header("🔢 Input Your Parlays and Final Fight")

# Parlay 1
st.subheader("Parlay 1")
parlay1_odds = st.number_input("Parlay 1 Odds", value=6.00, step=0.01)
parlay1_stake = st.number_input("Parlay 1 Stake", value=20.0, step=1.0)

# Parlay 2
st.subheader("Parlay 2")
parlay2_odds = st.number_input("Parlay 2 Odds", value=8.82, step=0.01)
parlay2_stake = st.number_input("Parlay 2 Stake", value=20.0, step=1.0)

# Final Fight (Hedge leg)
st.subheader("💥 Final Fight Details")
hedge_fighter = st.selectbox("Who are you hedging against? (e.g. Hill)", options=["Hill", "Other"])
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# Outcomes
st.subheader("🧮 Select Who Has Already Won")

p1_legs_hit = st.selectbox("✅ Parlay 1 - Legs before hedge all hit?", options=["Yes", "No"])
p2_legs_hit = st.selectbox("✅ Parlay 2 - Legs before hedge all hit?", options=["Yes", "No"])

# Run calc
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 20))
    data = []

    for hedge in hedge_steps:
        total_staked = parlay1_stake + parlay2_stake + hedge

        # If your hedged fighter wins (parlays lose, hedge hits)
        hedge_return = hedge * hedge_odds
        profit_hedge_win = hedge_return - total_staked

        # If your parlays hit (hedge loses)
        parlays_return = 0
        if p1_legs_hit == "Yes":
            parlays_return += parlay1_stake * parlay1_odds
        if p2_legs_hit == "Yes":
            parlays_return += parlay2_stake * parlay2_odds
        profit_parlay_win = parlays_return - total_staked

        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_staked,
            "Return if Hedge Wins": round(hedge_return, 2),
            "Profit if Hedge Wins": round(profit_hedge_win, 2),
            "Return if Parlays Win": round(parlays_return, 2),
            "Profit if Parlays Win": round(profit_parlay_win, 2),
        })

    df = pd.DataFrame(data)
    st.success("✅ Hedge Matrix Generated:")
    df_display = df.copy()
    for col in df.columns:
        if "Return" in col or "Profit" in col or "Wagered" in col:
            df_display[col] = df[col].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_display)
