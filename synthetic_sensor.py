import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# ==========================================
# HIVEMQ CONFIGURATION
# ==========================================

BROKER = "b0477e8631844e838120824baaf19132.s1.eu.hivemq.cloud"
PORT = 8883

USERNAME = "KARAN KUMAR"
PASSWORD = "Kkr@1234"

TOPIC = "compressed_air/sensors"


# ==========================================
# CONNECT CALLBACK
# ==========================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    print("--------------------------------")
    print("HiveMQ connection result:", reason_code)

    if reason_code == 0:
        print("CONNECTED TO HIVEMQ SUCCESSFULLY")
    else:
        print("CONNECTION FAILED")


# ==========================================
# MQTT CLIENT
# ==========================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="synthetic_air_sensor"
)

client.username_pw_set(
    USERNAME,
    PASSWORD
)

client.tls_set()

client.on_connect = on_connect


# ==========================================
# CONNECT
# ==========================================

print("Connecting to HiveMQ...")

client.connect(
    BROKER,
    PORT,
    60
)

client.loop_start()

time.sleep(2)


# ==========================================
# GENERATE SENSOR DATA
# ==========================================

while True:

    # Normal operating conditions
    pressure = random.uniform(6.8, 7.5)
    flow = random.uniform(80, 115)
    temperature = random.uniform(25, 35)
    power = random.uniform(3.5, 5.0)

    # Randomly create an abnormal/leak condition
    leak_condition = random.random() < 0.20

    if leak_condition:

        pressure = random.uniform(5.5, 6.4)
        flow = random.uniform(130, 170)
        power = random.uniform(5.0, 7.0)

        status = "SIMULATED_LEAK"

    else:

        status = "NORMAL"

    data = {

        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "pressure_bar": round(pressure, 2),

        "flow_lpm": round(flow, 2),

        "temperature_c": round(temperature, 2),

        "power_kw": round(power, 2),

        "simulated_status": status
    }

    message = json.dumps(data)

    print()
    print("Publishing:")
    print(message)

    result = client.publish(
        TOPIC,
        message,
        qos=1
    )

    print("Publish result:", result.rc)

    time.sleep(3)