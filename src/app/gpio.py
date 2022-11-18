import asyncio
import board
from keypad import Keys


async def poll_buttons():
    with Keys(
        (board.BUTTON_UP, board.BUTTON_DOWN), value_when_pressed=False, pull=True
    ) as keys:
        while True:
            key_event = keys.events.get()
            if key_event and key_event.pressed:
                key_number = key_event.key_number
                print("button", key_number)
            await asyncio.sleep(0.001)
