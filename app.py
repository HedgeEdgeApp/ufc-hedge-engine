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
final_fight_index = None

for i in range(num_bets):
    st.markdown(f"---")
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    st.markdown(f"#### {name}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    won = st.selectbox(f"✅ {name} – win?", options=["Yes", "No"], key=f"result_{i}")
    is_final = st.checkbox("☑️ Is this the final fight you want to hedge?", key=f"final_{i}")
    if is_final:
        final_fight_index = i
    bets.append({'name': name, 'odds': odds, 'stake': stake, 'won': won, 'is_final': is_final})

hedge_fighter = ""
hedge_odds = 0

if final_fight_index is not None:
    st.subheader("💥 Hedge Setup for Final Fight")
    hedge_fighter = st.text_input("Who are you hedging with if this bet loses? (e.g. Smith)", value="Smith")
    hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# Run calc
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    # Identify final bet
    final_bet = bets[final_fight_index] if final_fight_index is not None else None
    original_fighter = final_bet['name'] if final_bet else "Original"
    hedge_name = hedge_fighter or "Hedge"

    for hedge in hedge_steps:
        total_bets_stake = sum(bet['stake'] for bet in bets)
        total_staked = total_bets_stake + hedge

        hedge_return = hedge * hedge_odds
        profit_hedge_win = hedge_return - total_staked

        bets_return = sum(bet['stake'] * bet['odds'] for bet in bets if bet['won'] == "Yes")
        profit_bets_win = bets_return - total_staked

        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_staked,
            f"Return if {original_fighter} (Original) Wins": round(bets_return, 2),
            f"Profit if {original_fighter} (Original) Wins": round(profit_bets_win, 2),
            f"Return if {hedge_name} (Hedge) Wins": round(hedge_return, 2),
            f"Profit if {hedge_name} (Hedge) Wins": round(profit_hedge_win, 2),
        })

    df = pd.DataFrame(data)

    # 💡 Scenario summary goes ABOVE the table
    scenario_summary = []
    for i, bet in enumerate(bets):
        if i == final_fight_index:
            scenario_summary.append(f"{bet['name']} ❓")
        else:
            scenario_summary.append(f"{bet['name']} {'✅' if bet['won'] == 'Yes' else '❌'}")

    if scenario_summary:
        st.markdown(f"**Scenario:** {' | '.join(scenario_summary)}")

    st.success("✅ Hedge Matrix Generated:")
    df_display = df.copy()
    for col in df.columns:
        if (
            "Return" in col
            or "Profit" in col
            or "Wagered" in col
            or "Hedge Stake" in col
        ):
            df_display[col] = df[col].apply(lambda x: f"${x:,.2f}")

    st.dataframe(df_display) 
 
