#!/usr/bin/env python

import datetime
import logging
import os
import sys


class add_path:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass


def run_tests():
    plugin_path = os.path.abspath("../../../../../../../Plugins/PowerView.indigoPlugin/")
    logging.getLogger("Plugin").info("Starting PowerView Tests")  # log to Indigo Event Log

    logger = logging.getLogger('net.segment7.powerview')  # most of the logging during the tests go to a file
    fh = logging.FileHandler(os.path.join(plugin_path, "../../Logs/net.segment7.powerview/pvTestReport.log"))
    log_format = "{asctime}.{msecs:.0f}\t{levelname}  \t{funcName} {message}"
    fh.setFormatter(logging.Formatter(fmt=log_format, datefmt='%Y-%m-%d %H:%M:%S', style="{"))
    logger.addHandler(fh)
    logger.setLevel("DEBUG")

    now = datetime.datetime.now()
    os.chdir(plugin_path)
    logger.error("Run Tests at {} with cwd: {}".format(now.strftime("%Y-%m-%d %H:%M:%S"), os.getcwd()))

    with add_path(os.path.abspath("./Contents/Server Plugin/pv_tests/")):
        logger.error("Sys.path={}\n\n".format(sys.path))
        import pv_runner  # Will be found now that the folder has been added to the sys.path.

        try:
            pv_runner.run_tests()
        except Exception:
            logger.exception("Run Tests: Tests Failed")

    logger.info("Run Tests: Tests Complete")
    logging.getLogger("Plugin").info("PowerView Tests Complete. See pvTestReport.log in the PowerView Logs folder for details.")


if __name__ == '__main__':
    run_tests()
