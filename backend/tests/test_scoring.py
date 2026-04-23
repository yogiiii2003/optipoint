from app.services.scoring import haversine_km, weighted_score


def test_haversine_same_point_is_zero() -> None:
    assert haversine_km((0.0, 0.0), (0.0, 0.0)) == 0.0


def test_haversine_known_distance() -> None:
    d = haversine_km((18.5204, 73.8567), (18.5304, 73.8567))
    assert 1.0 < d < 1.3


def test_weighted_score_zero_distance_is_one() -> None:
    assert weighted_score({"hospital": 0.0}, {"hospital": 10}) == 1.0


def test_weighted_score_decreases_with_distance() -> None:
    near = weighted_score({"hospital": 1.0}, {"hospital": 10})
    far = weighted_score({"hospital": 10.0}, {"hospital": 10})
    assert near > far


def test_weighted_score_missing_category_returns_zero() -> None:
    assert weighted_score({}, {"hospital": 10}) == 0.0
