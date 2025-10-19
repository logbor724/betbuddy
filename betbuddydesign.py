import streamlit as st
from datetime import datetime
import bestBetBackend  # your backend file

# ----------------------------
# Sidebar setup and colors
# ----------------------------
sports = {
    "NFL": {"icon": "🏈", "hue": 120},
    "NBA": {"icon": "🏀", "hue": 0},
    "MLB": {"icon": "⚾", "hue": 210}
}

st.sidebar.title("Select a sport!")
selected_sport = st.sidebar.selectbox("Sport:", list(sports.keys()))

# Gradient styling
hue = sports[selected_sport]["hue"]
sat = 50
bg_gradient = f"linear-gradient(hsl({hue},{sat}%,15%), hsl({hue},{sat}%,25%))"
sidebar_gradient = f"linear-gradient(hsl({hue},{sat}%,20%), hsl({hue},{sat}%,30%))"

st.markdown(
    f"""
    <style>
        .stApp {{
            background: {bg_gradient};
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background: {sidebar_gradient};
        }}
        .stTextInput>div>div>input {{
            background: linear-gradient(to right, #1f1f1f, #2c2c2c);
            border: 1px solid #444;
            color: #fff;
            border-radius: 12px;
            padding: 10px;
            font-size: 16px;
            transition: all 0.2s ease;
        }}
        .stTextInput>div>div>input:focus {{
            border-color: #888;
            box-shadow: 0 0 8px #555 inset;
        }}
        .stButton>button {{
            background-color: #555; 
            color: #fff;
            border-radius: 6px;
            padding: 5px 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title(f"BetBuddy {sports[selected_sport]['icon']}")
st.write(f"Todays Date: {datetime.now().strftime('%b %d, %Y')}")

# ----------------------------
# Chatbot (unchanged)
# ----------------------------
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

chat_input = st.text_input("Ask for picks:", key="chat_input")

# ----------------------------
# Upcoming games section
# ----------------------------
st.subheader(f"Upcoming {selected_sport} Games")

# Button to fetch data
if st.button("Fetch Games and Predictions"):
    with st.spinner("Fetching Games and Predictions..."):
        data = BestBetBackend.main()

        if selected_sport == "NFL":
            games = data["nflGames"]
            winners = data["nflWinners"]
            reasons = data["nflReasoning"]
        elif selected_sport == "NBA":
            games = data["nbaGames"]
            winners = data["nbaWinners"]
            reasons = data["nbaReasoning"]
        else:
            games = data["mlbGames"]
            winners = data["mlbWinners"]
            reasons = data["mlbReasoning"]

        st.success(f"{selected_sport} Predictions Generated!")

        for i in range(len(games)):
            st.markdown(f"### {games[i]}")
            st.markdown(f"**BestBet:** {winners[i]}")
            st.caption(reasons[i])

# Default message
else:
    st.info(f"Click the button above to fetch upcoming {selected_sport} games and predictions.")

