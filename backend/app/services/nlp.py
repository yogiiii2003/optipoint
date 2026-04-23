import spacy

AMENITY_WEIGHTS: dict[str, int] = {
    "bus_stop": 20,
    "train_station": 15,
    "hospital": 18,
    "supermarket": 17,
    "pharmacy": 10,
    "school": 8,
    "restaurant": 7,
    "police_station": 6,
    "fire_station": 5,
    "cafe": 4,
    "shopping_mall": 4,
    "park": 4,
    "university": 3,
    "library": 2,
    "movie_theater": 2,
    "museum": 2,
}

_nlp = spacy.load("en_core_web_sm")


def extract_location(user_input: str) -> list[str]:
    doc = _nlp(user_input)
    return [tok.text for tok in doc if tok.pos_ == "PROPN"]


def extract_preferences(user_input: str) -> tuple[dict[str, int], dict[str, int]]:
    doc = _nlp(user_input)
    preferences = {tok.lemma_: 1 for tok in doc if tok.lemma_ in AMENITY_WEIGHTS}
    if preferences:
        weights = dict.fromkeys(AMENITY_WEIGHTS, 0)
        for pref in preferences:
            weights[pref] = AMENITY_WEIGHTS[pref]
    else:
        weights = AMENITY_WEIGHTS.copy()
    return weights, preferences
