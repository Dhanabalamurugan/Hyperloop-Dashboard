import paho.mqtt.client as mqtt
from datetime import datetime
import queue
mqtt_queue = queue.Queue()

def mqtt_on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print("MESSAGE ARRIVED:", payload)

    mqtt_queue.put({
        "data": payload,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })