"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Sample user profiles. Change active_profile to quickly test different tastes.
    # Copilot Chat suggested multiple profiles/presets to test different recommendation scenarios.
    profile_presets = {
        "happy_pop": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.80,
            "valence": 0.82,
            "danceability": 0.84,
            "acousticness": 0.20,
            "tempo_bpm": 122,
        },
        "chill_lofi": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.38,
            "valence": 0.60,
            "danceability": 0.58,
            "acousticness": 0.82,
            "tempo_bpm": 78,
        },
        "intense_rock": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.92,
            "valence": 0.46,
            "danceability": 0.64,
            "acousticness": 0.10,
            "tempo_bpm": 150,
        },
    }

    active_profile = "happy_pop"
    user_prefs = profile_presets[active_profile]

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
