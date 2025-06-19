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
    st.markdown(f"---")
    name = st.text_input(f"Name for Bet #{i+1}", value=f"Bet {i+1}", key=f"name_{i}")
    st.markdown(f"#### {name}")
    odds = st.number_input(f"{name} Odds", value=2.00, step=0.01, key=f"odds_{i}")
    stake = st.number_input(f"{name} Stake ($)", value=20.0, step=1.0, format="%.2f", key=f"stake_{i}")
    won = st.selectbox(f"✅ {name} – win?", options=["Yes", "No"], key=f"result_{i}")
    hedge_flag = st.checkbox("☑️ This bet depends on the final fight outcome (subject to hedge)", key=f"hedge_{i}")
    bets.append({'name': name, 'odds': odds, 'stake': stake, 'won': won, 'hedge': hedge_flag})

# 💥 Final Fight Details
st.subheader("💥 Final Fight Details")
hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)", value="Smith")
hedge_odds = st.number_input("Hedge Odds (Decimal)", value=2.30, step=0.01)

# Run calc
if st.button("🧠 Calculate Hedge Table"):
    hedge_steps = list(range(0, 301, 10))
    data = []

    # Partition the bets
    active_bets = [bet for bet in bets if bet["won"] == "Yes"]
    hedge_bets = [bet for bet in active_bets if bet["hedge"]]
    safe_bets = [bet for bet in active_bets if not bet["hedge"]]

    # Total returns if original wins (hedged bets win too)
    original_return = sum(bet["stake"] * bet["odds"] for bet in active_bets)

    for hedge in hedge_steps:
        total_staked = sum(bet["stake"] for bet in bets) + hedge

        # If hedge wins (original/hedge-linked bets lose)
        hedge_return = hedge * hedge_odds
        hedge_loss = sum(bet["stake"] for bet in hedge_bets)
        hedge_safe_win = sum(bet["stake"] * bet["odds"] for bet in safe_bets)
        profit_hedge_win = hedge_return + hedge_safe_win - total_staked

        profit_original_win = original_return - total_staked

        data.append({
            "Hedge Stake": hedge,
            "Total Wagered": total_staked,
            f"Return if Original Wins": round(original_return, 2),
            f"Profit if Original Wins": round(profit_original_win, 2),
            f"Return if {hedge_fighter} (Hedge) Wins": round(hedge_return + hedge_safe_win, 2),
            f"Profit if {hedge_fighter} (Hedge) Wins": round(profit_hedge_win, 2),
        })

    df = pd.DataFrame(data)

    # 💬 Scenario summary
    scenario_summary = []
    for bet in bets:
        if bet["hedge"]:
            outcome = "❓" if bet["won"] == "Yes" else "❌"
        else:
            outcome = "✅" if bet["won"] == "Yes" else "❌"
        scenario_summary.append(f"{bet['name']} {outcome}")

    st.markdown("### 🧾 Scenario")
    st.markdown(" | ".join(scenario_summary))

    # 💰 Format and display table
    st.success("✅ Hedge Matrix Generated:")
    df_display = df.copy()
    for col in df.columns:
        if "Return" in col or "Profit" in col or "Wagered" in col or "Hedge Stake" in col:
            df_display[col] = df[col].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_display) 
