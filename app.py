import pandas as pd
import streamlit as st

def calculate_hedge_matrix(live_bets, hedge_odds, hedge_fighter, max_hedge=300):
    hedge_stakes = list(range(0, max_hedge + 10, 10))
    results = []

    for hedge_stake in hedge_stakes:
        total_wagered = sum(bet["stake"] for bet in live_bets) + hedge_stake

        return_if_original = sum(
            bet["return"] for bet in live_bets if bet["win"] == "Yes"
        )
        profit_if_original = return_if_original - total_wagered

        return_if_hedge = hedge_stake * hedge_odds
        profit_if_hedge = return_if_hedge - total_wagered

        results.append({
            "Hedge Stake": f"${hedge_stake:.2f}",
            "Total Wagered": f"${total_wagered:.2f}",
            f"Return if {hedge_fighter} (Original) Wins": f"${return_if_original:.2f}",
            f"Profit if {hedge_fighter} (Original) Wins": f"${profit_if_original:.2f}",
            f"Return if {hedge_fighter} (Hedge) Wins": f"${return_if_hedge:.2f}",
            f"Profit if {hedge_fighter} (Hedge) Wins": f"${profit_if_hedge:.2f}",
        })

    return pd.DataFrame(results)

st.title("💸 UFC Hedge Engine")

bets = []
num_bets = st.number_input("How many bets do you want to input?", 1, 10, 3)

for i in range(num_bets):
    with st.expander(f"Bet #{i+1}", expanded=True):
        bet_name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet #{i+1}", key=f"name_{i}")
        fighter = st.text_input("Fighter or Parlay Description", key=f"fighter_{i}")
        stake = st.number_input("Stake", min_value=0.0, value=10.0, step=1.0, key=f"stake_{i}")
        odds = st.number_input("Odds (Decimal)", min_value=1.01, value=2.00, step=0.01, key=f"odds_{i}")
        outcome = st.selectbox("Did this bet win?", ["TBD", "Yes", "No"], key=f"outcome_{i}")
        is_final_fight = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"final_fight_{i}")

        bets.append({
            "name": bet_name,
            "fighter": fighter,
            "stake": stake,
            "odds": odds,
            "return": stake * odds,
            "win": outcome,
            "subject_to_hedge": is_final_fight
        })

hedge_section_visible = any(bet["subject_to_hedge"] for bet in bets)

if hedge_section_visible:
    st.markdown("### Final Fight Details")
    hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
    hedge_odds = st.number_input("Odds for hedge fighter", min_value=1.01, value=2.00, step=0.01)

    if hedge_fighter:
        scenario_summary = "Scenario: "
        scenario_summary += " / ".join(
            f"{bet['fighter']} ✅" if bet["win"] == "Yes"
            else f"{bet['fighter']} ❌" if bet["win"] == "No"
            else f"{bet['fighter']} ❓"
            for bet in bets if not bet["subject_to_hedge"]
        )
        st.markdown(f"#### {scenario_summary}")

        live_bets = [bet for bet in bets if bet["subject_to_hedge"] or bet["win"] == "Yes"]

        hedge_df = calculate_hedge_matrix(live_bets, hedge_odds, hedge_fighter)

        st.dataframe(
            hedge_df,
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("ℹ️ Select 'This bet depends on the final outcome' for at least one bet to enable hedging options.")
