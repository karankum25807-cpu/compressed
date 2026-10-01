import sqlite3
import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# ==========================================
# DATABASE
# ==========================================

DB_FILE = "data/compressed_air.db"

MODEL_DIR = "model"

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "energy_loss_model.pkl"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# ==========================================
# LOAD DATA
# ==========================================

connection = sqlite3.connect(DB_FILE)

df = pd.read_sql_query(
    "SELECT * FROM sensor_data",
    connection
)

connection.close()


if len(df) < 20:

    print("Not enough data for ML training.")

    print(
        "Run synthetic_sensor.py for some time "
        "and collect at least 20 records."
    )

    exit()


# ==========================================
# CREATE LABEL
# ==========================================

# Prototype label:
# pressure < 6.5 AND flow > 125 = loss

df["energy_loss"] = (

    (df["pressure_bar"] < 6.5)

    &

    (df["flow_lpm"] > 125)

).astype(int)


# ==========================================
# FEATURES
# ==========================================

features = [

    "pressure_bar",
    "flow_lpm",
    "temperature_c",
    "power_kw"

]

X = df[features]

y = df["energy_loss"]


# ==========================================
# TRAIN / TEST
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y

)


# ==========================================
# RANDOM FOREST
# ==========================================

model = RandomForestClassifier(

    n_estimators=100,

    random_state=42,

    class_weight="balanced"

)


model.fit(
    X_train,
    y_train
)


# ==========================================
# TEST
# ==========================================

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)


print()
print("===================================")
print("AI/ML MODEL TRAINING")
print("===================================")

print(
    "Accuracy:",
    round(accuracy * 100, 2),
    "%"
)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    model,
    MODEL_FILE
)

print()
print("Model saved:")
print(MODEL_FILE)