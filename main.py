import os
import sys
from contextlib import contextmanager

import pystray
from PIL import Image
from pystray import MenuItem as item

from factory import create_app


image = Image.open("resources/icon.png")
menu = (item("Stop", lambda icon: close(icon)),)
icon = pystray.Icon("name", image, "title", menu)


def close(icon):
    icon.stop()
    os._exit(0)


def show_notification(icon):
    icon.visible = True
    icon.notify("The backend is running on http://localhost:5000", title="MiniFeed")


@contextmanager
def suppress_stdout():
    with open("stdout.txt", "w+") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


with suppress_stdout():
    app = create_app()

    import logging

    logging.basicConfig(filename="error.log", level=logging.DEBUG)

    if __name__ == "__main__":
        icon.run_detached(setup=show_notification)

        app.run(port=5000)
