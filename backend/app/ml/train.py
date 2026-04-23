"""One-shot training script. Run: `python -m app.ml.train`."""
from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "universities.csv"
MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    X = df.drop(["Name", "Optimality", "Latitude", "Longitude"], axis=1)
    y = df["Optimality"].map({"Optimal": 0, "Not Optimal": 1})

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", VotingClassifier(
            estimators=[
                ("dt", DecisionTreeClassifier(random_state=42)),
                ("lr", LogisticRegression(max_iter=1000)),
                ("rf", RandomForestClassifier(random_state=42)),
            ],
            voting="soft",
        )),
    ])
    pipeline.fit(X_train, y_train)

    acc = pipeline.score(X_test, y_test)
    print(f"Test accuracy: {acc:.3f}")

    with MODEL_PATH.open("wb") as f:
        pickle.dump({"pipeline": pipeline, "feature_order": list(X.columns)}, f)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
