import asyncio


def on_mqtt_message(client, topic, message):
    print(f"MQTT > Message: Topic={topic} | Message={message}")


def on_mqtt_connect(client, userdata, flags, rc):
    print("MQTT > Connected: Flags={} | RC={}".format(flags, rc))


def on_mqtt_disconnect(client, userdata, rc):
    print("MQTT > Disconnected")


async def mqtt_poll(client, timeout=0.000001):
    while True:
        client.loop(timeout=timeout)
        await asyncio.sleep(timeout)
