import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Hedge Engine", layout="wide")
st.title("🤼 Sports Betting Hedge Engine")
st.markdown("---")

# Store all bets
bets = []

# Number of bets
num_bets = st.number_input("How many bets do you want to enter?", min_value=1, step=1, value=1)

# Collect each bet's data (stacked layout)
for i in range(num_bets):
    st.markdown(f"### 🧾 Bet #{i+1}")
    name = st.text_input(f"Bet #{i+1} Name", key=f"name_{i}")
    odds = st.number_input("Odds", min_value=1.0, step=0.01, key=f"odds_{i}")
    stake = st.number_input("Stake ($)", min_value=0.0, step=1.0, key=f"stake_{i}")
    result = st.selectbox("Did it win?", ["TBD", "Yes", "No"], key=f"result_{i}")
    subject_to_hedge = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_dependent_{i}")

    bets.append({
        "name": name,
        "odds": odds,
        "stake": stake,
        "result": result,
        "subject_to_hedge": subject_to_hedge
    })

# Final fight hedge details
st.markdown("### 💥 Final Fight Details")
hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
hedge_odds = st.number_input("Odds for hedge fighter", min_value=1.0, step=0.01)

# Hedge matrix generation
max_hedge = 300
rows = []

for hedge_stake in range(0, max_hedge + 1, 10):
    total_staked = sum(bet["stake"] for bet in bets) + hedge_stake

    # Original fighter outcome
    original_returns = 0
    forimport streamlit as st
import pandas as pd

# --------------------------
# Page Config and Title
# --------------------------
st.set_page_config(page_title="UFC Hedge Engine", layout="wide")
st.title("💥 UFC Hedge Engine")

# --------------------------
# Sidebar Settings for Hedge Stake
# --------------------------
st.sidebar.header("⚙️ Hedge Stake Settings")

hedge_step = st.sidebar.number_input("Step Size ($)", min_value=1.0, max_value=500.0, value=10.0, step=1.0)
hedge_max = st.sidebar.number_input("Max Hedge Stake ($)", min_value=10.0, max_value=5000.0, value=300.0, step=10.0)

# --------------------------
# Sample Bets Input Section
# --------------------------
st.subheader("Your Bets")
bets = []
num_bets = st.number_input("How many bets?", min_value=1, max_value=10, value=3, step=1)

for i in range(num_bets):
    st.markdown(f"### 🧾 Bet #{i+1}")
    col1, col2, col3 = st.columns([4, 2, 2])
    with col1:
        bet_name = st.text_input(f"Name (Bet #{i+1})", key=f"name_{i}")
    with col2:
        odds = st.number_input(f"Odds", min_value=1.01, step=0.01, key=f"odds_{i}")
    with col3:
        stake = st.number_input(f"Stake ($)", min_value=0.0, step=1.0, key=f"stake_{i}")

    win_status = st.selectbox(
        "Has this bet won?",
        options=["TBD", "Yes", "No"],
        key=f"win_{i}",
    )

    is_final_fight = st.checkbox("This bet depends on the final outcome (subject to hedge)", key=f"hedge_flag_{i}")

    bets.append({
        "name": bet_name,
        "odds": odds,
        "stake": stake,
        "win": win_status,
        "hedge_target": is_final_fight,
    })

# --------------------------
# Final Fight Hedge Input
# --------------------------
st.subheader("💣 Final Fight Details")
col1, col2 = st.columns(2)
with col1:
    hedge_fighter = st.text_input("Who are you hedging on in the final fight? (e.g. Smith)")
with col2:
    hedge_odds = st.number_input("Odds for hedge fighter", min_value=1.01, step=0.01, value=2.0)

# --------------------------
# Scenario Summary Header
# --------------------------
tbd_icon = "❓"
tick_icon = "✅"
x_icon = "❌"
scenario_summary = "Scenario: "

for bet in bets:
    if bet["win"] == "Yes":
        icon = tick_icon
    elif bet["win"] == "No":
        icon = x_icon
    else:
        icon = tbd_icon
    scenario_summary += f'{bet["name"]} {icon} / '

scenario_summary = scenario_summary.rstrip(" / ")
st.markdown(f"### {scenario_summary}")

# --------------------------
# Calculate Table
# --------------------------
st.subheader("📊 Hedge Outcome Table")

stake_range = list(range(0, int(hedge_max + hedge_step), int(hedge_step)))
rows = []

for hedge_stake in stake_range:
    total_wagered = sum(b["stake"] for b in bets) + hedge_stake

    original_return = 0
    hedge_return = hedge_stake * hedge_odds

    for b in bets:
        if b["win"] == "Yes":
            original_return += b["stake"] * b["odds"]
        elif b["win"] == "TBD" and b["hedge_target"]:
            original_return += b["stake"] * b["odds"]

    original_profit = original_return - total_wagered
    hedge_profit = hedge_return - total_wagered if all(
        (b["win"] == "No" or (b["win"] == "TBD" and b["hedge_target"])) for b in bets if b["hedge_target"]
    ) else 0 - total_wagered

    rows.append({
        "Hedge Stake": f"${hedge_stake:.2f}",
        "Total Wagered": f"${total_wagered:.2f}",
        f"Return if Original Fighter Wins": f"${original_return:.2f}",
        f"Profit if Original Fighter Wins": f"${original_profit:.2f}",
        f"Return if {hedge_fighter} (Hedge) Wins": f"${hedge_return:.2f}",
        f"Profit if {hedge_fighter} (Hedge) Wins": f"${hedge_profit:.2f}",
    })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)
