import csv
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored_songs = []
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

        for song in self.songs:
            score, _reasons = score_song(user_prefs, song)
            scored_songs.append((song, score))

        scored_songs.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _score in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        _score, reasons = score_song(user_prefs, song)
        return "; ".join(reasons) if reasons else "No matching signals found."


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")

    numeric_fields = {
        "id": int,
        "energy": float,
        "tempo_bpm": float,
        "valence": float,
        "danceability": float,
        "acousticness": float,
    }

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if not row:
                continue

            song: Dict = {}
            for key, value in row.items():
                if value is None:
                    song[key] = value
                    continue

                cleaned_value = value.strip()
                if cleaned_value == "":
                    song[key] = cleaned_value
                elif key in numeric_fields:
                    song[key] = numeric_fields[key](cleaned_value)
                else:
                    song[key] = cleaned_value

            songs.append(song)
    print(f"Loaded {len(songs)} songs.")
    return songs


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored_songs: List[Tuple[Dict, float, str]] = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "No matching signals found."
        scored_songs.append((song, score, explanation))

    return sorted(scored_songs, key=lambda item: item[1], reverse=True)[:k]


def _get_value(source: Any, *keys: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        for key in keys:
            if key in source:
                return source[key]
    else:
        for key in keys:
            if hasattr(source, key):
                return getattr(source, key)
    return default


def _normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value).strip().lower()


def _similarity(
    song_value: Optional[float],
    target_value: Optional[float],
    tolerance: float = 1.0,
) -> float:
    if song_value is None or target_value is None:
        return 0.0
    return max(
        0.0, 1.0 - min(abs(float(song_value) - float(target_value)) / tolerance, 1.0)
    )


def score_song(user_prefs, song):
    """Return a normalized score and a list of human-readable reasons."""
    score = 0.0
    max_score = 0.0
    reasons = []

    song_genre = _normalize_text(_get_value(song, "genre"))
    song_mood = _normalize_text(_get_value(song, "mood"))
    song_energy = _get_value(song, "energy")
    song_tempo = _get_value(song, "tempo_bpm")
    song_valence = _get_value(song, "valence")
    song_danceability = _get_value(song, "danceability")
    song_acousticness = _get_value(song, "acousticness")

    genre_target = _normalize_text(_get_value(user_prefs, "genre", "favorite_genre"))
    if genre_target:
        max_score += 2.0
        if song_genre == genre_target:
            score += 2.0
            reasons.append("genre match (+2.0)")

    mood_target = _normalize_text(_get_value(user_prefs, "mood", "favorite_mood"))
    if mood_target:
        max_score += 1.0
        if song_mood == mood_target:
            score += 1.0
            reasons.append("mood match (+1.0)")

    energy_target = _get_value(user_prefs, "energy", "target_energy")
    if energy_target is not None:
        max_score += 2.0
        energy_similarity = _similarity(song_energy, energy_target)
        energy_points = 2.0 * energy_similarity
        score += energy_points
        reasons.append(f"energy similarity (+{energy_points:.2f})")

    tempo_target = _get_value(user_prefs, "tempo_bpm")
    if tempo_target is not None:
        max_score += 1.0
        tempo_similarity = _similarity(song_tempo, tempo_target, tolerance=40.0)
        tempo_points = 1.0 * tempo_similarity
        score += tempo_points
        reasons.append(f"tempo similarity (+{tempo_points:.2f})")

    valence_target = _get_value(user_prefs, "valence")
    if valence_target is not None:
        max_score += 1.0
        valence_similarity = _similarity(song_valence, valence_target)
        valence_points = 1.0 * valence_similarity
        score += valence_points
        reasons.append(f"valence similarity (+{valence_points:.2f})")

    danceability_target = _get_value(user_prefs, "danceability")
    if danceability_target is not None:
        max_score += 0.5
        danceability_similarity = _similarity(song_danceability, danceability_target)
        danceability_points = 0.5 * danceability_similarity
        score += danceability_points
        reasons.append(f"danceability similarity (+{danceability_points:.2f})")

    acousticness_target = _get_value(user_prefs, "acousticness")
    likes_acoustic = _get_value(user_prefs, "likes_acoustic")
    if acousticness_target is not None:
        max_score += 0.5
        acousticness_similarity = _similarity(song_acousticness, acousticness_target)
        acousticness_points = 0.5 * acousticness_similarity
        score += acousticness_points
        reasons.append(f"acousticness similarity (+{acousticness_points:.2f})")
    elif likes_acoustic is not None:
        max_score += 0.5
        likes_acoustic = bool(likes_acoustic)
        acoustic_bonus = (
            0.5
            if (
                (
                    likes_acoustic
                    and song_acousticness is not None
                    and song_acousticness >= 0.5
                )
                or (
                    not likes_acoustic
                    and song_acousticness is not None
                    and song_acousticness < 0.5
                )
            )
            else 0.0
        )
        score += acoustic_bonus
        if acoustic_bonus > 0:
            reasons.append(f"acousticness preference (+{acoustic_bonus:.2f})")

    normalized_score = score / max_score if max_score > 0 else 0.0
    return normalized_score, reasons
