import paho.mqtt.client as mqtt
import json
import time
import random

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883, 60)

print("Publisher connected...")

print("Publishing Hyperloop Pod Data...\n")

while True:
    pod_data = {
        "id": f"Pod-{random.randint(1,6)}",
        "speed": random.randint(600, 1200),
        "battery": random.randint(20, 100),
        "status": random.choice(["Operational", "Maintenance", "Docked"])
    }

    client.publish("hyperloop/pods/demo", json.dumps(pod_data))
    print("Published:", pod_data)

    time.sleep(2)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to broker.hivemq.com successfully")
    else:
        print(f"❌ Connection failed with code {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.connect("broker.hivemq.com", 1883, 60)
client.loop_start()

