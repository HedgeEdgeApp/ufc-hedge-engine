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
    st.markdown("---")
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    st.markdown(f"#### {name}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    won = st.selectbox(f"✅ {name} – win?", options=["TBD", "Yes", "No"], key=f"result_{i}")
    subject_to_hedge = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_{i}")
    bets.append({'name': name, 'odds': odds, 'stake': stake, 'won': won, 'subject_to_hedge': subject_to_hedge})

# 💥 Final Fight Details
st.subheader("💥 Final Fight Details")
hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# 🧮 Calculate
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    for hedge in hedge_steps:
        total_bets_stake = sum(bet['stake'] for bet in bets)
        total_staked = total_bets_stake + hedge

        # Sum all non-TBD bets that have won
        bets_return = sum(bet['stake'] * bet['odds'] for bet in bets if bet['won'] == "Yes")
        
        # Include TBD bets ONLY IF they are not subject to the final fight hedge
        bets_return += sum(
            bet['stake'] * bet['odds']
            for bet in bets
            if bet['won'] == "TBD" and not bet['subject_to_hedge']
        )

        # Hedge return (if all subject-to-hedge bets are assumed lost and hedge hits)
        hedge_return = hedge * hedge_odds
        profit_bets_win = bets_return - total_staked
        profit_hedge_win = hedge_return - total_staked

        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_staked,
            "Return if Original Fighter Wins": round(bets_return, 2),
            "Profit if Original Fighter Wins": round(profit_bets_win, 2),
            f"Return if {hedge_fighter} (Hedge) Wins": round(hedge_return, 2),
            f"Profit if {hedge_fighter} (Hedge) Wins": round(profit_hedge_win, 2),
        })

    df = pd.DataFrame(data)

    # Format with currency
    df_display = df.copy()
    for col in df_display.columns:
        if (
            "Return" in col
            or "Profit" in col
            or "Wagered" in col
            or "Hedge Stake" in col
        ):
            df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}")

    # ✅ Set Hedge Stake as index for fixed position on far left
    df_display.set_index("Hedge Stake", inplace=True)

    # 🧾 Scenario Summary (above table)
    scenario_summary = []
    for bet in bets:
        if bet["won"] == "Yes":
            scenario_summary.append(f"{bet['name']} ✅")
        elif bet["won"] == "No":
            scenario_summary.append(f"{bet['name']} ❌")
        else:
            scenario_summary.append(f"{bet['name']} ❓")

    if scenario_summary:
        st.markdown(f"**Scenario:** {' | '.join(scenario_summary)}")

    # 📊 Show table
    st.success("✅ Hedge Matrix Generated:")
    st.dataframe(df_display)
 
 
