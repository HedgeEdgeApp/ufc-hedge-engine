import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Hedge Engine", layout="wide")

st.title("💸 UFC Hedge Engine")

# Initialize session state
if "bets" not in st.session_state:
    st.session_state.bets = []

st.markdown("### ➕ Add Your Bets")

with st.form("bet_form"):
    col1, col2, col3 = st.columns([1.2, 2, 1.5])
    with col1:
        bet_name = st.text_input("Bet name (e.g. Bet #1)")
        odds = st.number_input("Odds", min_value=1.01, value=2.00)
        stake = st.number_input("Stake ($)", min_value=0.01, value=10.0)
    with col2:
        fighters = st.text_input("Fighter(s) in bet", placeholder="e.g. Fiziev or Allen/Edwards")
        win_status = st.selectbox("Did this bet win?", ["TBD", "Yes", "No"])
    with col3:
        final_flag = st.checkbox("🎯 This bet depends on the final outcome (subject to hedge)")

    submitted = st.form_submit_button("Add Bet")
    if submitted and bet_name and fighters:
        st.session_state.bets.append({
            "name": bet_name,
            "fighters": fighters,
            "odds": odds,
            "stake": stake,
            "result": win_status,
            "final": final_flag,
        })

# Bets Table
if st.session_state.bets:
    st.markdown("### 📋 Current Bets")
    df = pd.DataFrame(st.session_state.bets)
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.markdown("### 💥 Final Fight Details")

    hedge_fighter = st.text_input("Who are you hedging **on** in the final fight?")
    hedge_odds = st.number_input("Odds of hedge bet", min_value=1.01, value=2.00)
    hedge_unit = st.number_input("💵 Hedge Stake Unit", min_value=1, value=10, step=1)

    st.markdown("### 🧾 Scenario")
    scenario = []
    for bet in st.session_state.bets:
        icon = "✅" if bet["result"] == "Yes" else "❌" if bet["result"] == "No" else "❓"
        scenario.append(f"{bet['fighters']} {icon}")
    st.markdown(", ".join(scenario))

    st.markdown("### 📊 Hedge Table")

    rows = []
    for hedge in range(0, 301, hedge_unit):
        total_wagered = sum(b["stake"] for b in st.session_state.bets) + hedge
        return_if_original = sum(
            b["stake"] * b["odds"]
            for b in st.session_state.bets
            if b["result"] == "Yes" or (b["result"] == "TBD" and b["final"])
        )
        return_if_hedge = hedge * hedge_odds
        profit_if_original = return_if_original - total_wagered
        profit_if_hedge = return_if_hedge - total_wagered

        rows.append({
            "Hedge Stake": f"${hedge}",
            "Total Wagered": f"${total_wagered:.2f}",
            "Return if Original Wins": f"${return_if_original:.2f}",
            "Profit if Original Wins": f"${profit_if_original:.2f}",
            f"Return if {hedge_fighter} (Hedge) Wins": f"${return_if_hedge:.2f}",
            f"Profit if {hedge_fighter} (Hedge) Wins": f"${profit_if_hedge:.2f}",
        })

    table = pd.DataFrame(rows)
    st.dataframe(table, use_container_width=True, hide_index=True)

if st.button("🔄 Reset All"):
    st.session_state.bets = []
    st.experimental_rerun()
