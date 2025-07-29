import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Sports Betting Hedge Engine", layout="wide")

# Display banner image (optional)
st.image("hedge_edge_banner.png", use_container_width=True)

st.markdown("---")

# Store all bets
bets = []

# Number of bets
num_bets = st.number_input("How many bets do you want to enter?", min_value=1, step=1, value=1)

# Collect each bet's data (stacked layout)
for i in range(num_bets):
    st.markdown(f"### ℹ️ Bet #{i+1}")
    name = st.text_input(f"Bet #{i+1} Name", key=f"name_{i}")
    odds = st.number_input("Odds", min_value=1.0, step=0.01, key=f"odds_{i}")
    stake = st.number_input("Stake ($)", min_value=0.0, step=1.0, key=f"stake_{i}")
    result = st.selectbox("Did it win?", ["TBD", "Yes", "No"], key=f"result_{i}")
    subject_to_hedge = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_dependent_{i}")
    hedge_side_exposure = st.checkbox("This bet includes the hedge fighter (hedge side exposure)", key=f"hedge_side_{i}")
    bonus_cash = st.checkbox("Was this bet placed using bonus cash? ℹ️", key=f"bonus_cash_{i}")
    if bonus_cash:
        st.caption("\- Bonus bets will not count toward 'Total Wagered' and returns/profits will only include winnings (no stake)")

    bets.append({
        "name": name,
        "odds": odds,
        "stake": stake,
        "result": result,
        "subject_to_hedge": subject_to_hedge,
        "hedge_side_exposure": hedge_side_exposure,
        "bonus_cash": bonus_cash
    })

# Final Event Details
st.markdown("### 💣 Final Event Details")
col1, col2 = st.columns(2)
fighter_a = col1.text_input("Fighter A (Original Side)", key="fighter_a")
fighter_b = col2.text_input("Fighter B (Hedge Side)", key="fighter_b")

hedge_fighter = fighter_b
hedge_odds = st.number_input("Odds for the hedge event", min_value=1.0, step=0.01)

# Hedge Stake Unit Selector
hedge_unit = st.number_input("Hedge Stake Unit ($)", min_value=1, step=1, value=10)
max_hedge = st.number_input("Maximum Hedge Stake ($)", min_value=hedge_unit, step=hedge_unit, value=300)

# Warning at the end of Final Event Details
st.warning("🚨 If you change the hedge fighter in the 'Final Event Details', make sure to revisit and update the checkboxes in each bet. Accurate results depend on the correct use of 'subject to hedge' and 'hedge side exposure'.")

# Helper function to compute real return (excluding bonus stake for bonus bets)
def adjusted_return(bet):
    if bet["result"] not in ["Yes", "TBD"]:
        return 0
    if bet["bonus_cash"]:
        return bet["stake"] * (bet["odds"] - 1)
    return bet["stake"] * bet["odds"]

# Determine if any bet is affected by the hedge
any_hedge_bets = any(bet["subject_to_hedge"] for bet in bets)

# Hedge matrix generation
rows = []
real_return_a = bonus_return_a = real_return_b = bonus_return_b = 0

if any_hedge_bets:
    for hedge_stake in range(0, max_hedge + 1, hedge_unit):
        total_staked = sum(bet["stake"] for bet in bets if not bet["bonus_cash"]) + hedge_stake

        # Return if Fighter A wins
        fighter_a_returns = sum(
            adjusted_return(bet)
            for bet in bets
            if not bet["hedge_side_exposure"] and (bet["result"] in ["Yes", "TBD"])
        )

        # Return if Fighter B wins
        fighter_b_returns = sum(
            adjusted_return(bet)
            for bet in bets
            if (bet["hedge_side_exposure"] or not bet["subject_to_hedge"]) and (bet["result"] in ["Yes", "TBD"])
        )

        hedge_return = hedge_stake * hedge_odds
        profit_if_a = fighter_a_returns - total_staked
        profit_if_b = hedge_return + fighter_b_returns - total_staked

        real_return_a = sum(
            adjusted_return(bet)
            for bet in bets
            if not bet["bonus_cash"] and not bet["hedge_side_exposure"] and bet["result"] in ["Yes", "TBD"]
        )
        bonus_return_a = fighter_a_returns - real_return_a

        real_return_b = sum(
            adjusted_return(bet)
            for bet in bets
            if not bet["bonus_cash"] and (bet["hedge_side_exposure"] or not bet["subject_to_hedge"]) and bet["result"] in ["Yes", "TBD"]
        )
        bonus_return_b = fighter_b_returns - real_return_b

        rows.append({
            "Hedge Stake": f"${hedge_stake:.2f}",
            "Total Wagered": f"${total_staked:.2f}",
            f"Return if {fighter_a} (Original) Wins": f"${fighter_a_returns:.2f}",
            f"Profit if {fighter_a} (Original) Wins": f"${profit_if_a:.2f}",
            f"Return if {fighter_b} (Hedge) Wins": f"${hedge_return + fighter_b_returns:.2f}",
            f"Profit if {fighter_b} (Hedge) Wins": f"${profit_if_b:.2f}"
        })
else:
    st.info("ℹ️ None of your bets are affected by the final event, so hedging scenarios are not applicable.")
    total_staked = sum(bet["stake"] for bet in bets if not bet["bonus_cash"])
    fighter_a_returns = sum(adjusted_return(bet) for bet in bets if bet["result"] in ["Yes", "TBD"])
    profit_if_a = fighter_a_returns - total_staked

    real_return_a = sum(adjusted_return(bet) for bet in bets if bet["result"] in ["Yes", "TBD"] and not bet["bonus_cash"])
    bonus_return_a = fighter_a_returns - real_return_a
    real_return_b = real_return_a
    bonus_return_b = bonus_return_a

    rows.append({
        "Hedge Stake": "$0.00",
        "Total Wagered": f"${total_staked:.2f}",
        f"Return if {fighter_a} (Original) Wins": f"${fighter_a_returns:.2f}",
        f"Profit if {fighter_a} (Original) Wins": f"${profit_if_a:.2f}",
        f"Return if {fighter_b} (Hedge) Wins": f"${fighter_a_returns:.2f}",
        f"Profit if {fighter_b} (Hedge) Wins": f"${profit_if_a:.2f}"
    })

df = pd.DataFrame(rows)

# Scenario Summary
scenario_parts = []
for bet in bets:
    if bet["result"] == "Yes":
        emoji = "WIN"
    elif bet["result"] == "No":
        emoji = "LOSS"
    else:
        emoji = "TBD"
    bc_flag = " (Bonus)" if bet["bonus_cash"] else ""
    scenario_parts.append(f"{bet['name']}{bc_flag} {emoji}")

scenario_text = f"Scenario: {' / '.join(scenario_parts)}"

st.markdown("### 💥 Scenario Summary")
st.markdown(f"**{scenario_text}**")

# Clarifying message for user context (placed just below scenario summary)
if fighter_a and fighter_b:
    st.info(f"💬 You are currently hedging on **{fighter_b}**. All other returns are attributed to **{fighter_a} (Original Side)**.")

# Show hedge matrix
st.dataframe(df, hide_index=True, use_container_width=True)

# Download CSV button including scenario summary
csv_buffer = io.StringIO()
csv_buffer.write(scenario_text + "\n")
df.to_csv(csv_buffer, index=False)
csv_data = csv_buffer.getvalue().encode("utf-8")

st.download_button(
    label="⬇️ Export Hedge Table as CSV",
    data=csv_data,
    file_name="hedge_table.csv",
    mime="text/csv"
)

# Bonus Breakdown Section
st.markdown("### 📊 Bonus vs Real Return Breakdown")
summary_df = pd.DataFrame({
    "Component": ["Real Return", "Bonus Return"],
    f"If {fighter_a} Wins": [f"${real_return_a:.2f}", f"${bonus_return_a:.2f}"],
    f"If {fighter_b} Wins": [f"${real_return_b:.2f}", f"${bonus_return_b:.2f}"]
})
st.dataframe(summary_df, hide_index=True, use_container_width=True)
