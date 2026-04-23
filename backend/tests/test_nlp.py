from app.services.nlp import AMENITY_WEIGHTS, extract_location, extract_preferences


def test_extract_location_finds_proper_nouns():
    locations = extract_location("find an apartment in Pune near a hospital")
    assert "Pune" in locations


def test_extract_preferences_detects_mentioned_amenities():
    weights, prefs = extract_preferences("I want a place near hospital and supermarket")
    assert "hospital" in prefs
    assert "supermarket" in prefs
    assert weights["hospital"] == AMENITY_WEIGHTS["hospital"]
    assert weights["supermarket"] == AMENITY_WEIGHTS["supermarket"]
    assert weights["museum"] == 0


def test_extract_preferences_falls_back_to_defaults_when_none_matched():
    weights, prefs = extract_preferences("I want a nice place to live")
    assert prefs == {}
    assert weights == AMENITY_WEIGHTS
