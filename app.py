import streamlit as st
import pandas as pd

# Title
st.title("🧠 UFC Hedge Engine")

st.markdown("This tool helps you calculate hedge options based on your bet outcomes and the final fight of the night.")

# User Inputs
st.header("🔢 Input Your Bets and Final Fight")

# Bet 1
bet1_name = st.text_input("Name for Bet 1", value="Bet 1")
st.subheader(bet1_name)
bet1_odds = st.number_input(f"{bet1_name} Odds", value=6.00, step=0.01)
bet1_stake = st.number_input(f"{bet1_name} Stake ($)", value=20.0, step=1.0, format="%.2f")


# Bet 2
bet2_name = st.text_input("Name for Bet 2", value="Bet 2")
st.subheader(bet2_name)
bet2_odds = st.number_input(f"{bet2_name} Odds", value=8.82, step=0.01)
bet2_stake = st.number_input(f"{bet2_name} Stake ($)", value=20.0, step=1.0, format="%.2f")


# Final Fight (Hedge leg)
st.subheader("💥 Final Fight Details")
hedge_fighter = st.selectbox("Who are you hedging against? (e.g. Hill)", options=["Hill", "Other"])
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# Outcomes
st.subheader("🧮 Select Who Has Already Won")

bet1_legs_hit = st.selectbox("✅ Bet 1 - Legs before hedge all hit?", options=["Yes", "No"])
bet2_legs_hit = st.selectbox("✅ Bet 2 - Legs before hedge all hit?", options=["Yes", "No"])

# Run calc
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    for hedge in hedge_steps:
        total_staked = bet1_stake + bet2_stake + hedge

        # If your hedged fighter wins (bets lose, hedge hits)
        hedge_return = hedge * hedge_odds
        profit_hedge_win = hedge_return - total_staked

        # If your parlays hit (hedge loses)
        bets_return = 0
        if bet1_legs_hit == "Yes":
            bets_return += bet1_stake * bet1_odds
        if bet2_legs_hit == "Yes":
            bets_return += bet2_stake * bet2_odds
        profit_bets_win = bets_return - total_staked

        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_staked,
            "Return if Hedge Wins": round(hedge_return, 2),
            "Profit if Hedge Wins": round(profit_hedge_win, 2),
            "Return if Bets Win": round(bets_return, 2),
            "Profit if Bets Win": round(profit_bets_win, 2),
        })

    df = pd.DataFrame(data)
    st.success("✅ Hedge Matrix Generated:")
    df_display = df.copy()
    for col in df.columns:
        if "Return" in col or "Profit" in col or "Wagered" in col:
            df_display[col] = df[col].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_display)
