#!/usr/bin/python3

import contextlib
import datetime
import logging
import logging.handlers
import os
import sys
try:
    import indigo
except ImportError:
    pass


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


def run_tests(hub3, hub2):
    now = datetime.datetime.now()
    # Scripts run from Menu Items start with cwd:
    # /Library/Application Support/Perceptive Automation/Indigo 2022.2/IndigoPluginHost3.app/
    #       Contents/Resources/PlugIns/ScriptExecutor.indigoPlugin/Contents/Server Plugin
    indigo_base = os.path.abspath("../../../../../../../")
    # indigo_base = os.path.abspath("/Library/Application Support/Perceptive Automation/Indigo 2022.2")
    plugin_path = os.path.abspath(os.path.join(indigo_base, "Plugins/PowerView.indigoPlugin/"))

    test_details_file_name = os.path.join(indigo_base, "Logs/net.segment7.powerview/pvTestDetails.log")
    fh = logging.handlers.TimedRotatingFileHandler(test_details_file_name, when='midnight', backupCount=10, encoding='utf-8')
    log_format = "%(asctime)s.%(msecs).0f)\t%(levelname)s \t%(funcName)s\t\t%(message)s"
    fh.setFormatter(logging.Formatter(fmt=log_format, datefmt='%y-%m-%d %H:%M:%S'))
    fh.setLevel(logging.DEBUG)
    logger = logging.getLogger("wsgmac.com.test.powerview")  # most of the logging during the tests go to a file
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    os.chdir(plugin_path)
    logger.debug("Run Tests at {} with hub3={} and hub2={}".format(now.strftime("%Y-%m-%d %H:%M:%S"), hub3, hub2))

    with add_path(os.path.abspath("./Contents/Server Plugin/pv_tests/")):
        logger.debug("Sys.path={}\n\n".format(sys.path))
        import pv_runner  # Will be found now that the folder has been added to the sys.path.

        try:
            with open(os.path.join(indigo_base, "Logs/net.segment7.powerview/pvTestReport.log"), 'w') as std_file:
                with contextlib.redirect_stdout(std_file):
                    passed, failed, errored, skipped = pv_runner.run_tests(hub3, hub2)
        except:
            logger.exception("Run Tests: Tests Failed")

    logger.debug("Run Tests: Tests Complete")
    logger.debug("==============================================================================\n\n\n")

    return passed, failed, errored, skipped


if __name__ == '__main__':
    indigo.server.log("Run Tests: Starting PowerView Tests", level=logging.INFO)  # log to Indigo Event Log

    count_passed, count_failed, count_errored, count_skipped = run_tests(hub3=None, hub2=None)
    
    if count_failed == 0 and count_errored == 0:
        indigo.server.log(f"PowerView Tests Complete. All tests PASSED.", level=logging.INFO)
    else:
        indigo.server.log(f"PowerView Tests Complete. Passed: {count_passed}, Failed: {count_failed}" +
                          (f", Broken: {count_errored}" if count_errored else "") +
                          (f", Skipped: {count_skipped}" if count_skipped else "") +
                          ". See pvTestReport.log in the PowerView Logs folder for details.", level=logging.INFO)
