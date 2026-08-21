
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def train_and_predict(df: pd.DataFrame):
    X = df[["rainfall","traffic","road_age"]]
    y = df["label"]
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X,y)
    df["risk"] = model.predict_proba(X)[:,1]
    return df.sort_values("risk", ascending=False)
