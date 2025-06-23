import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Hedge Engine", layout="wide")

# Title and Instructions
st.title("🧠 UFC Hedge Engine")
st.markdown("""
This tool helps you calculate hedge outcomes based on your bets and the final fight of the night.

👉 For best results on mobile, **pin the "Hedge Stake" column** using the ⚙️ menu in the top-right of the table.
""")

# User Inputs
st.header("🔢 Input Your Bets")

num_bets = st.number_input("How many bets?", min_value=1, max_value=10, value=1, step=1)
bets = []
final_bet_index = None

for i in range(num_bets):
    st.markdown(f"---")
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    st.markdown(f"#### {name}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    result = st.selectbox(f"{name} – Win?", options=["TBD", "Yes", "No"], key=f"result_{i}")
    is_final = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"final_{i}")

    if is_final:
        final_bet_index = i  # last one checked will be treated as final fight

    bets.append({
        'name': name,
        'odds': odds,
        'stake': stake,
        'won': result,
        'is_final': is_final
    })

# Final Fight Details
if final_bet_index is not None:
    st.subheader("💥 Final Fight Details")
    hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)", value="Smith")
    hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.00, step=0.01)
else:
    hedge_fighter = None

# Calculate button
if st.button("🧮 Calculate Hedge Table") and hedge_fighter:
    hedge_steps = list(range(0, 301, 10))
    data = []

    # Pre-compute win amounts
    base_bets_return = sum(b['stake'] * b['odds'] for b in bets if b['won'] == "Yes")
    tbd_bets = [b for b in bets if b['is_final']]

    for hedge in hedge_steps:
        hedge_return = hedge * hedge_odds
        total_stake = hedge + sum(b['stake'] for b in bets)

        # Return if original (TBD) bets hit
        tbd_return = sum(b['stake'] * b['odds'] for b in tbd_bets)
        original_total_return = base_bets_return + tbd_return
        profit_if_original = original_total_return - total_stake

        # Return if hedge hits (original bets lose)
        hedge_total_return = hedge_return + base_bets_return
        profit_if_hedge = hedge_total_return - total_stake

        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_stake,
            f"Return if Original Fighter Wins": round(original_total_return, 2),
            f"Profit if Original Fighter Wins": round(profit_if_original, 2),
            f"Return if {hedge_fighter} (Hedge) Wins": round(hedge_total_return, 2),
            f"Profit if {hedge_fighter} (Hedge) Wins": round(profit_if_hedge, 2),
        })

    df = pd.DataFrame(data)

    # Format as currency
    df_display = df.copy()
    for col in df.columns:
        if "Return" in col or "Profit" in col or "Wagered" in col or "Hedge Stake" in col:
            df_display[col] = df[col].apply(lambda x: f"${x:,.2f}")

    # Display Scenario Summary (above table)
    st.markdown("### 🎯 Scenario Summary")
    scenario_summary = []
    for bet in bets:
        if bet['won'] == "Yes":
            symbol = "✅"
        elif bet['won'] == "No":
            symbol = "❌"
        else:
            symbol = "❓"
        scenario_summary.append(f"{bet['name']} {symbol}")
    st.markdown(" | ".join(scenario_summary))

    # Display table
    st.markdown("### 📊 Hedge Table")
    st.dataframe(df_display, hide_index=True)  
