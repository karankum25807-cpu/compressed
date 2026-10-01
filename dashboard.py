import streamlit as st
import sqlite3
import pandas as pd
import joblib
import os
import time
from datetime import datetime

import plotly.express as px


# ==========================================
# PAGE
# ==========================================

st.set_page_config(
    page_title="Compressed Air Energy Loss Detection",
    page_icon="💨",
    layout="wide"
)


st.title(
    "💨 Compressed Air Energy Loss Detection System"
)

st.caption(
    "Synthetic Sensor → MQTT → HiveMQ → SQLite → AI/ML → Dashboard → Alert"
)


# ==========================================
# FILES
# ==========================================

DB_FILE = "data/compressed_air.db"

MODEL_FILE = "model/energy_loss_model.pkl"


# ==========================================
# CHECK DATABASE
# ==========================================

if not os.path.exists(DB_FILE):

    st.warning(
        "Waiting for sensor data..."
    )

    st.stop()


# ==========================================
# LOAD DATABASE
# ==========================================

connection = sqlite3.connect(
    DB_FILE
)

df = pd.read_sql_query(
    """
    SELECT *
    FROM sensor_data
    ORDER BY id ASC
    """,
    connection
)

connection.close()


if df.empty:

    st.warning(
        "No sensor data available."
    )

    st.stop()


# ==========================================
# ML PREDICTION
# ==========================================

if os.path.exists(MODEL_FILE):

    model = joblib.load(
        MODEL_FILE
    )

    features = [

        "pressure_bar",
        "flow_lpm",
        "temperature_c",
        "power_kw"

    ]

    df["prediction"] = model.predict(
        df[features]
    )

    df["prediction_probability"] = model.predict_proba(
        df[features]
    )[:, 1]

else:

    df["prediction"] = 0

    df["prediction_probability"] = 0


# ==========================================
# CURRENT READING
# ==========================================

latest = df.iloc[-1]


pressure = latest["pressure_bar"]

flow = latest["flow_lpm"]

temperature = latest["temperature_c"]

power = latest["power_kw"]

prediction = int(
    latest["prediction"]
)

probability = float(
    latest["prediction_probability"]
)


# ==========================================
# METRICS
# ==========================================

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Pressure",
    f"{pressure:.2f} bar"
)


col2.metric(
    "Flow",
    f"{flow:.2f} L/min"
)


col3.metric(
    "Temperature",
    f"{temperature:.2f} °C"
)


col4.metric(
    "Power",
    f"{power:.2f} kW"
)


# ==========================================
# ALERT
# ==========================================

st.subheader("System Status")


if prediction == 1:

    st.error(
        f"🚨 COMPRESSED AIR ENERGY LOSS DETECTED\n\n"
        f"ML probability: {probability * 100:.1f}%"
    )

    # Write alert
    with open(
        "alerts.log",
        "a"
    ) as file:

        file.write(
            f"{datetime.now()} - "
            f"ENERGY LOSS DETECTED - "
            f"Pressure={pressure:.2f} bar, "
            f"Flow={flow:.2f} L/min, "
            f"Power={power:.2f} kW\n"
        )

else:

    st.success(
        f"✅ SYSTEM NORMAL\n\n"
        f"ML probability of loss: {probability * 100:.1f}%"
    )


# ==========================================
# PRESSURE GRAPH
# ==========================================

st.subheader("Pressure")

fig_pressure = px.line(

    df,

    x="timestamp",

    y="pressure_bar",

    title="Compressed Air Pressure"

)

st.plotly_chart(
    fig_pressure,
    use_container_width=True
)


# ==========================================
# FLOW GRAPH
# ==========================================

st.subheader("Flow")

fig_flow = px.line(

    df,

    x="timestamp",

    y="flow_lpm",

    title="Compressed Air Flow"

)

st.plotly_chart(
    fig_flow,
    use_container_width=True
)


# ==========================================
# POWER GRAPH
# ==========================================

st.subheader("Power")

fig_power = px.line(

    df,

    x="timestamp",

    y="power_kw",

    title="Compressor Power"

)

st.plotly_chart(
    fig_power,
    use_container_width=True
)


# ==========================================
# TEMPERATURE
# ==========================================

st.subheader("Temperature")

fig_temperature = px.line(

    df,

    x="timestamp",

    y="temperature_c",

    title="Temperature"

)

st.plotly_chart(

    fig_temperature,

    use_container_width=True

)


# ==========================================
# DATA TABLE
# ==========================================

st.subheader(
    "Latest Sensor Data"
)

st.dataframe(
    df.tail(20),
    use_container_width=True
)


# ==========================================
# AUTO REFRESH
# ==========================================

time.sleep(3)

st.rerun()