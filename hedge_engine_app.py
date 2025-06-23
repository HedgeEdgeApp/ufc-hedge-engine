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
    st.markdown(f"---")  # separator
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    st.markdown(f"#### {name}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    won = st.selectbox(f"✅ {name} – win?", options=["TBD", "Yes", "No"], key=f"result_{i}")
    hedge_flag = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_flag_{i}")
    
    bets.append({
        'name': name,
        'odds': odds,
        'stake': stake,
        'won': won,
        'subject_to_hedge': hedge_flag
    })

# 💥 Final Fight Details
st.subheader("💥 Final Fight Details")
hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# 🧠 Run calc
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    for hedge in hedge_steps:
        # Group bets
        confirmed_winners = [b for b in bets if b['won'] == "Yes"]
        hedge_subjects = [b for b in bets if b['subject_to_hedge']]
        
        stake_confirmed = sum(b['stake'] for b in confirmed_winners)
        return_confirmed = sum(b['stake'] * b['odds'] for b in confirmed_winners)

        stake_hedged = sum(b['stake'] for b in hedge_subjects)
        return_hedged = sum(b['stake'] * b['odds'] for b in hedge_subjects)

        total_staked = stake_confirmed + stake_hedged + hedge

        # Outcome: original fighter wins
        return_if_original = return_confirmed + return_hedged
        profit_if_original = return_if_original - total_staked

        # Outcome: hedge fighter wins
        return_if_hedge = return_confirmed + (hedge * hedge_odds)
        profit_if_hedge = return_if_hedge - total_staked

        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_staked,
            "Return if Original Fighter Wins": round(return_if_original, 2),
            "Profit if Original Fighter Wins": round(profit_if_original, 2),
            f"Return if {hedge_fighter} (Hedge) Wins": round(return_if_hedge, 2),
            f"Profit if {hedge_fighter} (Hedge) Wins": round(profit_if_hedge, 2),
        })

    df = pd.DataFrame(data)

    # Format columns
    df_display = df.copy()
    for col in df_display.columns:
        if "Return" in col or "Profit" in col or "Wagered" in col or "Hedge Stake" in col:
            df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}")

    # ✅ Set 'Hedge Stake' as index to appear fixed on far left
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
    st.dataframe(df_display, use_container_width=True)
