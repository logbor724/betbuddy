import streamlit as st
from datetime import datetime
import os
import bestBetBackend  # your backend file
from openai import OpenAI

# ----------------------------
# OpenAI client
# ----------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
st.write(f"Today's Date: {datetime.now().strftime('%b %d, %Y')}")

# ----------------------------
# Chatbot setup
# ----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("🏈 Chat with BetBuddy AI")

chat_input = st.text_input("Ask about sports, predictions, or stats:")

if chat_input:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": chat_input})
    with st.chat_message("user"):
        st.markdown(chat_input)

    user_text = chat_input.lower()
    response_text = ""

    # Detect sport keyword and fetch backend predictions
    if "nfl" in user_text:
        games = bestBetBackend.get_upcoming_games("NFL")
        winners = bestBetBackend.analyze_matchups("NFL", games)
        reasons = bestBetBackend.matchup_reasoning("NFL", list(zip(games, winners)))

        response_text = "**🏈 NFL Predictions:**\n\n"
        for g, w, r in zip(games, winners, reasons):
            response_text += f"- {g}\n  **Winner:** {w}\n  _Reason:_ {r}\n\n"

    elif "nba" in user_text:
        games = bestBetBackend.get_upcoming_games("NBA")
        winners = bestBetBackend.analyze_matchups("NBA", games)
        reasons = bestBetBackend.matchup_reasoning("NBA", list(zip(games, winners)))

        response_text = "**🏀 NBA Predictions:**\n\n"
        for g, w, r in zip(games, winners, reasons):
            response_text += f"- {g}\n  **Winner:** {w}\n  _Reason:_ {r}\n\n"

    elif "mlb" in user_text:
        games = bestBetBackend.get_upcoming_games("MLB")
        winners = bestBetBackend.analyze_matchups("MLB", games)
        reasons = bestBetBackend.matchup_reasoning("MLB", list(zip(games, winners)))

        response_text = "**⚾ MLB Predictions:**\n\n"
        for g, w, r in zip(games, winners, reasons):
            response_text += f"- {g}\n  **Winner:** {w}\n  _Reason:_ {r}\n\n"

    else:
        # General sports AI response
        completion = client.responses.create(
            model="gpt-5-mini",
            input=f"You are BetBuddy AI, a friendly sports analyst. The user said: '{chat_input}'. "
                  "Reply conversationally about sports or predictions without gambling advice."
        )
        response_text = completion.output_text.strip()

    # Add AI response
    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)

# Display previous chat messages
for msg in st.session_state.chat_history:
    if msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("user"):
            st.markdown(msg["content"])

# ----------------------------
# Upcoming games section
# ----------------------------
st.subheader(f"Upcoming {selected_sport} Games")

if st.button("Fetch Games and Predictions"):
    with st.spinner("Fetching Games and Predictions..."):
        data = bestBetBackend.main()

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
else:
    st.info(f"Click the button above to fetch upcoming {selected_sport} games and predictions.")





