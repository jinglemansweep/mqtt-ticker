import asyncio
import board
from busio import I2C
import gc

# import json
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from adafruit_bitmap_font import bitmap_font
from adafruit_lis3dh import LIS3DH_I2C
from displayio import Group
from rtc import RTC
from secrets import secrets

from app.config import (
    DEBUG,
    NTP_ENABLE,
    NTP_INTERVAL,
    MATRIX_WIDTH,
    MATRIX_HEIGHT,
    MATRIX_BIT_DEPTH,
    MATRIX_COLOR_ORDER,
    MQTT_PREFIX,
)
from app.gpio import poll_buttons
from app.mqtt import mqtt_poll, on_mqtt_connect, on_mqtt_disconnect, on_mqtt_message
from app.utils import logger, matrix_rotation, parse_timestamp, global_test

logger(
    f"debug={DEBUG} ntp_enable={NTP_ENABLE} ntp_interval={NTP_INTERVAL} mqtt_prefix={MQTT_PREFIX}"
)
logger(
    f"matrix_width={MATRIX_WIDTH} matrix_height={MATRIX_HEIGHT} matrix_bit_depth={MATRIX_BIT_DEPTH} matrix_color_order={MATRIX_COLOR_ORDER}"
)

# CONSTANTS
BUTTON_UP = 0
BUTTON_DOWN = 1

# STATIC RESOURCES
logger("loading static resources")
font_bitocra = bitmap_font.load_font("/bitocra7.bdf")

# RGB MATRIX
logger("configuring rgb matrix")
matrix = Matrix(
    width=MATRIX_WIDTH,
    height=MATRIX_HEIGHT,
    bit_depth=MATRIX_BIT_DEPTH,
    color_order=MATRIX_COLOR_ORDER,
)
accelerometer = LIS3DH_I2C(I2C(board.SCL, board.SDA), address=0x19)
_ = accelerometer.acceleration  # drain startup readings

# DISPLAY / FRAMEBUFFER
logger("configuring display/framebuffer")
display = matrix.display
display.rotation = matrix_rotation(accelerometer)
display.show(Group())
gc.collect()

# NETWORKING
logger("configuring networking")
network = Network(status_neopixel=board.NEOPIXEL, debug=DEBUG)
network.connect()
mac = network._wifi.esp.MAC_address
device_id = "{:02x}{:02x}{:02x}{:02x}".format(mac[0], mac[1], mac[2], mac[3])
gc.collect()
# NETWORK TIME
if NTP_ENABLE:
    logger("setting date/time from network")
    timestamp = network.get_local_time()
    timetuple = parse_timestamp(timestamp)
    RTC().datetime = timetuple

# SHARED STATE


# MQTT
logger("configuring mqtt client")
MQTT.set_socket(socket, network._wifi.esp)
client = MQTT.MQTT(
    broker=secrets.get("mqtt_broker"),
    username=secrets.get("mqtt_user"),
    password=secrets.get("mqtt_password"),
    port=secrets.get("mqtt_port", 1883),
)
client.on_connect = on_mqtt_connect
client.on_disconnect = on_mqtt_disconnect
client.on_message = on_mqtt_message
client.connect()
gc.collect()


# EVENT LOOP
def run():
    logger("start asyncio event loop")
    gc.collect()
    while True:
        try:
            asyncio.run(main())
        finally:
            logger(f"asyncio crash, restarting")
            asyncio.new_event_loop()


async def main():
    logger("event loop started")
    global_test()
    asyncio.create_task(poll_buttons())
    asyncio.create_task(mqtt_poll(client))
    client.subscribe(f"matrixportal/{device_id}/#", 1)
    gc.collect()
    while True:
        await tick()
        await asyncio.sleep(0.0001)


async def tick():
    logger("tick")
    await asyncio.sleep(1)
    gc.collect()


# STARTUP

run()
