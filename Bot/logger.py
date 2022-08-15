import logging


def initLogger(level=logging.DEBUG):
    if level == logging.DEBUG:
        # Display more stuff when in a debug mode
        logging.basicConfig(
            format='%(asctime)s - %(module)s - %(levelname)s - %(message)s',
            level=level)
    else:
        # Display less stuff for info mode
        logging.basicConfig(format='%(levelname)s: %(message)s', level=level)
