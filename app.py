import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Hedge Engine", layout="wide")

st.title("🧠 UFC Hedge Engine")
st.markdown("Calculate potential hedge outcomes for your UFC bets.")

bets = []
num_bets = st.number_input("How many bets are you placing?", min_value=1, step=1, value=3)

for i in range(num_bets):
    st.markdown("---")
    with st.container():
        st.subheader(f"🧾 Bet #{i+1}")
        name = st.text_input(f"Name for Bet #{i+1}", key=f"name_{i}", value=f"Bet #{i+1}")
        odds = st.number_input(f"Odds for {name}", min_value=1.01, step=0.01, key=f"odds_{i}")
        stake = st.number_input(f"Stake for {name}", min_value=0.0, step=1.0, key=f"stake_{i}")
        win_state = st.selectbox(
            f"Did this bet win?", options=["TBD", "Yes", "No"], key=f"win_{i}"
        )
        is_final_fight = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_{i}")
        bets.append({
            "name": name,
            "odds": odds,
            "stake": stake,
            "win_state": win_state,
            "is_final": is_final_fight
        })

st.markdown("---")
st.subheader("💥 Final Fight Details")

col1, col2 = st.columns(2)
with col1:
    hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
with col2:
    hedge_odds = st.number_input("Odds of hedge fighter", min_value=1.01, step=0.01)

if hedge_fighter:
    st.markdown("---")
    st.subheader("📊 Outcome Table")

    hedge_range = range(0, 310, 10)
    table_rows = []

    # Build scenario text (above the table)
    scenario_text = "Scenario: "
    for bet in bets:
        if bet["win_state"] == "Yes":
            scenario_text += f"✅ {bet['name']} "
        elif bet["win_state"] == "No":
            scenario_text += f"❌ {bet['name']} "
        elif bet["win_state"] == "TBD" and bet["is_final"]:
            scenario_text += f"❓ {bet['name']} "

    st.markdown(f"**{scenario_text.strip()}**")

    for hedge_stake in hedge_range:
        total_wagered = sum(b["stake"] for b in bets) + hedge_stake

        return_if_original = 0
        return_if_hedge = 0

        for b in bets:
            if b["win_state"] == "Yes":
                return_if_original += b["stake"] * b["odds"]
            elif b["win_state"] == "TBD" and b["is_final"]:
                return_if_original += b["stake"] * b["odds"]

        for b in bets:
            if b["win_state"] == "TBD" and b["is_final"]:
                continue  # These lose if hedge wins
            elif b["win_state"] == "Yes":
                return_if_hedge += b["stake"] * b["odds"]

        return_if_hedge += hedge_stake * hedge_odds

        profit_if_original = return_if_original - total_wagered
        profit_if_hedge = return_if_hedge - total_wagered

        table_rows.append({
            "Hedge Stake": f"${hedge_stake:.2f}",
            "Total Wagered": f"${total_wagered:.2f}",
            f"Return if Original Fighter Wins": f"${return_if_original:.2f}",
            f"Profit if Original Fighter Wins": f"${profit_if_original:.2f}",
            f"Return if {hedge_fighter} (Hedge) Wins": f"${return_if_hedge:.2f}",
            f"Profit if {hedge_fighter} (Hedge) Wins": f"${profit_if_hedge:.2f}"
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
