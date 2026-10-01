import paho.mqtt.client as mqtt
import json
import sqlite3
import os


# ==========================================
# HIVEMQ CONFIGURATION
# ==========================================

BROKER = "b0477e8631844e838120824baaf19132.s1.eu.hivemq.cloud"
PORT = 8883

USERNAME = "KARAN KUMAR"
PASSWORD = "Kkr@1234"

TOPIC = "compressed_air/sensors"


# ==========================================
# DATABASE
# ==========================================

os.makedirs("data", exist_ok=True)

DB_FILE = "data/compressed_air.db"


def create_database():

    connection = sqlite3.connect(DB_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT,

            pressure_bar REAL,

            flow_lpm REAL,

            temperature_c REAL,

            power_kw REAL,

            simulated_status TEXT

        )
    """)

    connection.commit()

    connection.close()


create_database()


# ==========================================
# MQTT CONNECT
# ==========================================

def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties=None
):

    print("--------------------------------")
    print("HiveMQ connection result:", reason_code)

    if reason_code == 0:

        print("Connected to HiveMQ Cloud")

        result, mid = client.subscribe(
            TOPIC,
            qos=1
        )

        print("Subscribed to:", TOPIC)
        print("Subscribe result:", result)
        print("Waiting for sensor data...")

    else:

        print("Connection failed")


# ==========================================
# MQTT MESSAGE
# ==========================================

def on_message(client, userdata, message):

    print()
    print("===================================")
    print("SENSOR DATA RECEIVED")
    print("Topic:", message.topic)

    try:

        data = json.loads(
            message.payload.decode()
        )

        print(data)

        connection = sqlite3.connect(DB_FILE)

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO sensor_data
            (
                timestamp,
                pressure_bar,
                flow_lpm,
                temperature_c,
                power_kw,
                simulated_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (

            data["timestamp"],
            data["pressure_bar"],
            data["flow_lpm"],
            data["temperature_c"],
            data["power_kw"],
            data.get("simulated_status", "UNKNOWN")

        ))

        connection.commit()

        connection.close()

        print("Saved to SQLite")

    except Exception as error:

        print("ERROR:", error)


# ==========================================
# MQTT CLIENT
# ==========================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="compressed_air_sqlite_receiver"
)

client.username_pw_set(
    USERNAME,
    PASSWORD
)

client.tls_set()

client.on_connect = on_connect
client.on_message = on_message


# ==========================================
# START
# ==========================================

print("Connecting to HiveMQ...")

client.connect(
    BROKER,
    PORT,
    60
)

client.loop_forever()