import sys
import re
from openai import OpenAI
sys.stdout.reconfigure(encoding='utf-8')

# Do not push api key to github or streamlit cloud, it will shut the key off and im not making new ones
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get upcoming games for analysis
def get_upcoming_games(league, count=3):

    prompt = (
        f"Find {count} upcoming {league} games in the next week. "
        f"Use this exact format on each line: 'Away Team at Home Team - YYYY-MM-DD'. "
        "No bullets, no extra text, no explanations — just the lines."
    )

    response = client.responses.create(
        model="gpt-5",
        tools=[{"type": "web_search"}],
        input=prompt
    )

    text = response.output_text.strip()

    # Try to split into lines first
    games_list = [line.strip() for line in text.split("\n") if line.strip()]

    # If model returned everything in one line, break on periods or ' - '
    if len(games_list) <= 1:
        games_list = re.split(r"[.;]\s*|\s{2,}", text)
        games_list = [g.strip() for g in games_list if g.strip()]

    return games_list

# analyze matchups to determine most likely winner for each game
def analyze_matchups(league, games_list):
    games_text = "\n".join(f"{i+1}. {g}" for i, g in enumerate(games_list))
    prompt = (
        f"Consider these upcoming {league} games:\n{games_text}\n\n"
        "For each item (1..N), pick the more likely winner based on general team strength. "
        "No odds or betting language. Output EXACTLY one line per item like this:\n"
        "1) Winner: TEAM NAME"
    )

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    text = response.output_text.strip()

    # Split into list of winners
    winners = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if "Winner:" in line:
            winners.append(line.split("Winner:")[-1].strip())
        else:
            winners.append(line)

    return winners
#remove sources from reasoning
def remove_sources_from_reasoning(reason_list):
    """
    Removes any text after the first period in each reasoning line.
    Useful for trimming off citations or source references like [1†source].
    """
    cleaned = []
    for r in reason_list:
        if "." in r:
            cleaned.append(r.split(".")[0].strip() + ".")
        else:
            cleaned.append(r.strip())
    return cleaned
# Generate reasoning for predictions
def matchup_reasoning(league, matchups):
    """
    matchups = list of tuples (game, winner)
    """
    lines = [f"{i+1}. {g} -> Predicted winner: {w}" for i, (g, w) in enumerate(matchups)]
    matchups_text = "\n".join(lines)
    prompt = (
        f"Here are some upcoming {league} games and predicted winners:\n{matchups_text}\n\n"
        "Give a short, one-sentence reason for each prediction based on player stats, "
        "team performance, and recent matchups. Prioritize analytics from 2024-2025 season and the 25-26 season. Do not reference stats from 2023 or earlier. "
        "Be consise, your responses should be easy to read and digest while staying informative."
        "your response should only include text, commas, and periods. no dashes or additional punctuation/characters."
    )

    response = client.responses.create(
        model="gpt-5",
        tools=[{"type": "web_search"}],
        input=prompt
    )

    output = response.output_text.strip()

    # Split by newline or period-space to separate each explanation cleanly
    lines = [line.strip() for line in output.split("\n") if line.strip()]

    # If AI outputs all in one paragraph, try to split on periods
    if len(lines) < len(matchups):
        temp = [p.strip() for p in output.split('.') if len(p.strip()) > 3]
        lines = temp

    # Pad or truncate to match number of matchups
    if len(lines) < len(matchups):
        lines.extend(["No reasoning provided."] * (len(matchups) - len(lines)))
    elif len(lines) > len(matchups):
        lines = lines[:len(matchups)]

    lines = remove_sources_from_reasoning(lines)
    return lines



# main function, returns list for front-end access and prints to console for debugging
def main():
    nflGames, nflWinners, nflReasoning = [], [], []
    nbaGames, nbaWinners, nbaReasoning = [], [], []
    mlbGames, mlbWinners, mlbReasoning = [], [], []

    leagues = [
        ("NFL", nflGames, nflWinners, nflReasoning),
        ("NBA", nbaGames, nbaWinners, nbaReasoning),
        ("MLB", mlbGames, mlbWinners, mlbReasoning),
    ]

    for league, games, winners, reasons in leagues:
        print(f"\n--- {league} ---")

        # Step 1: Get matchups
        games_list = get_upcoming_games(league)
        games.extend(games_list)

        # Step 2: Predict winners
        winners_list = analyze_matchups(league, games_list)
        winners.extend(winners_list)

        # Step 3: Combine and reason
        matchups = list(zip(games_list, winners_list))
        reasons_list = matchup_reasoning(league, matchups)
        reasons.extend(reasons_list)

        print(f"\nFinal {league} summary:")
        for g, w, r in zip(games, winners, reasons):
            print(f"Matchup: {g}\nBestBet: {w}\nExplanation: {r}\n")
        print("-" * 40)

    print("\n=== Done ===")

    # Return all 3 leagues for frontend access
    return {
        "nflGames": nflGames,
        "nflWinners": nflWinners,
        "nflReasoning": nflReasoning,
        "nbaGames": nbaGames,
        "nbaWinners": nbaWinners,
        "nbaReasoning": nbaReasoning,
        "mlbGames": mlbGames,
        "mlbWinners": mlbWinners,
        "mlbReasoning": mlbReasoning
    }


if __name__ == "__main__":
    main()

