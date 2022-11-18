import gc

gc.collect()

print("Boot > Init: Mem={}".format(gc.mem_free()))

import displayio

displayio.release_displays()

import app
