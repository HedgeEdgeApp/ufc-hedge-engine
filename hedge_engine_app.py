import streamlit as st
import pandas as pd

# Title
st.title("🧠 Sport Hedge Engine")

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
    won = st.selectbox(f"✅ {name} – win?", options=["TBD", "Yes", "No"], index=0, key=f"result_{i}")
    is_hedged = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedged_{i}")
    bets.append({'name': name, 'odds': odds, 'stake': stake, 'won': won, 'hedged': is_hedged})

# 💥 Final Fight Details
st.subheader("💥 Final Fight Details")
hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)", value="Smith")
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# Run calc
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    for hedge in hedge_steps:
        total_bets_stake = sum(bet['stake'] for bet in bets)
        total_staked = total_bets_stake + hedge

        # If hedge wins (original fighter loses)
        hedge_return = hedge * hedge_odds
        profit_hedge_win = hedge_return - total_staked

        # If original fighter wins (hedge loses)
        bets_return = 0
        for bet in bets:
            if bet['won'] == "Yes":
                bets_return += bet['stake'] * bet['odds']
            elif bet['won'] == "TBD" and bet['hedged']:
                bets_return += bet['stake'] * bet['odds']
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

    st.markdown("### 🧾 Scenario Summary:")
    summary = []
    for bet in bets:
        symbol = "✅" if bet['won'] == "Yes" else "❌" if bet['won'] == "No" else "❓"
        summary.append(f"{bet['name']} {symbol}")
    st.markdown(" | ".join(summary))

    st.success("✅ Hedge Matrix Generated:")
    df_display = df.copy()
    for col in df.columns:
        if "Return" in col or "Profit" in col or "Wagered" in col or "Hedge Stake" in col:
            df_display[col] = df[col].apply(lambda x: f"${x:,.2f}")

    # Set column order
    ordered_cols = [
        "Hedge Stake",
        "Total Wagered",
        "Return if Original Fighter Wins",
        "Profit if Original Fighter Wins",
        f"Return if {hedge_fighter} (Hedge) Wins",
        f"Profit if {hedge_fighter} (Hedge) Wins"
    ]
    st.dataframe(df_display[ordered_cols]) 
