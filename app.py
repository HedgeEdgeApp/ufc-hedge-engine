
import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Hedge Engine", layout="wide")

# --- Sidebar: Final Fight Hedge Info ---
st.sidebar.header("🧨 Final Fight Details")
hedge_final_fight_selected = st.sidebar.checkbox("Is there a final fight you want to hedge?")
hedge_fighter = None
hedge_odds = None
if hedge_final_fight_selected:
    hedge_fighter = st.sidebar.text_input("Who are you hedging on in the final fight? (e.g. Smith)", "")
    hedge_odds = st.sidebar.number_input("Hedge fighter's odds (decimal)", min_value=1.01, step=0.01)

# --- Main App ---
st.title("💸 UFC Hedge Engine")

st.markdown("### ➕ Add your bets")
with st.form(key="bet_form"):
    bet_name = st.text_input("Bet name (e.g. Rountree ML, Parlay #2, Fiziev KO)", key="bet_name")
    odds = st.number_input("Odds", min_value=1.01, step=0.01, key="odds")
    stake = st.number_input("Stake ($)", min_value=0.0, step=1.0, key="stake")
    result = st.selectbox("Has this bet won?", ["TBD", "Yes", "No"], key="result")
    is_final_fight_bet = st.checkbox("This bet depends on the final outcome (subject to hedge)", key="hedge_checkbox")
    submit = st.form_submit_button("Add Bet")

if "bets" not in st.session_state:
    st.session_state.bets = []

if submit:
    st.session_state.bets.append({
        "bet_name": bet_name,
        "odds": odds,
        "stake": stake,
        "result": result,
        "is_final_fight_bet": is_final_fight_bet
    })

# Display current bets
if st.session_state.bets:
    st.markdown("### 🧾 Current Bets")
    for i, bet in enumerate(st.session_state.bets):
        st.write(f"**Bet #{i + 1}** — {bet['bet_name']} | Odds: {bet['odds']} | Stake: ${bet['stake']} | Won: {bet['result']} | Subject to Final Fight: {'✅' if bet['is_final_fight_bet'] else '❌'}")

# --- Scenario Summary ---
def get_status_emoji(result):
    if result == "Yes":
        return "✅"
    elif result == "No":
        return "❌"
    else:
        return "❓"

if st.session_state.bets:
    st.markdown("### 🎯 Scenario:")
    scenario_labels = []
    for bet in st.session_state.bets:
        if not bet['is_final_fight_bet']:
            label = f"{bet['bet_name']} {get_status_emoji(bet['result'])}"
            scenario_labels.append(label)
    st.markdown(" / ".join(scenario_labels))

# --- Hedge Stake Table Generator ---
def calculate_returns(hedge_unit, hedge_fighter, hedge_odds, final_fight_selected):
    rows = []
    for i in range(31):
        hedge_stake = i * hedge_unit
        total_wagered = hedge_stake + sum(bet["stake"] for bet in st.session_state.bets)

        original_return = 0.0
        hedge_return = hedge_stake * hedge_odds

        for bet in st.session_state.bets:
            won = bet["result"] == "Yes"
            if bet["is_final_fight_bet"]:
                if final_fight_selected:
                    if hedge_fighter and won:
                        original_return += bet["stake"] * bet["odds"]
                else:
                    original_return += bet["stake"] * bet["odds"] if won else 0
            else:
                original_return += bet["stake"] * bet["odds"] if won else 0
                if bet["result"] == "TBD":
                    total_wagered -= bet["stake"]

        original_profit = original_return - total_wagered
        hedge_profit = hedge_return - total_wagered

        rows.append({
            "Hedge Stake ($)": hedge_stake,
            f"Total Wagered ($)": total_wagered,
            f"Return if Original Fighter Wins ($)": original_return,
            f"Profit if Original Fighter Wins ($)": original_profit,
            f"Return if {hedge_fighter} (Hedge) Wins ($)": hedge_return,
            f"Profit if {hedge_fighter} (Hedge) Wins ($)": hedge_profit
        })
    return pd.DataFrame(rows)

# --- Hedge Stake Table Display ---
if hedge_final_fight_selected and hedge_fighter and hedge_odds and st.session_state.bets:
    st.markdown("### 💡 Choose Your Hedge Stake Unit")
    hedge_unit = st.number_input("Hedge Stake Unit ($)", min_value=1, max_value=500, value=10, step=1)
    st.markdown("### 📊 Hedge Outcome Matrix")

    df = calculate_returns(hedge_unit, hedge_fighter, hedge_odds, hedge_final_fight_selected)
    st.dataframe(df, hide_index=True, use_container_width=True)
