#!/usr/bin/env python

import indigo
import logging
import sys


def do_live_hub():
    hub3 = None
    hub2 = None

    menu_items = "../../../../../../../Plugins/PowerView.indigoPlugin/Contents/Menu Items"
    # ########### menu_items = "/Users/sfyfe/Documents/Projects/indigo-powerview/PowerView.indigoPlugin/Contents/Menu Items"
    sys.path.insert(1, menu_items)
    runner = __import__("Run Tests")

    for dev in indigo.devices.iter("net.segment7.powerview.PowerViewHub"):
        if dev.states.get('generation', 0) == 3:
            hub3 = dev.address

        elif dev.states.get('generation', 0) == 2:
            hub2 = dev.address

        else:
            logger.warning("PowerView Hub '{}' has not been updated with the latest PowerView plugin. Assuming it is a V2 hub.".format(dev.name))

    logger.debug(f"About to run tests with gen3 hub {hub3} and/or version 2 hub {hub2}.")
    return runner.run_tests(hub3, hub2)


if __name__ == '__main__':
    logger = logging.getLogger("wsgmac.com.test.powerview")
    indigo.server.log("Run Tests with Hub: Starting PowerView Tests", level=logging.INFO)  # log to Indigo Event Log
    logger.debug("'Run Tests with Hubs' begins, using live hubs, if available")
    count_passed, count_failed, count_errored, count_skipped = do_live_hub()
    
    if count_failed == 0 and count_errored == 0:
        indigo.server.log(f"PowerView Tests Complete. All tests PASSED.", level=logging.INFO)
    else:
        indigo.server.log(f"PowerView Tests Complete. Passed: {count_passed}, Failed: {count_failed}" +
                          (f", Broken: {count_errored}" if count_errored else "") +
                          (f", Skipped: {count_skipped}" if count_skipped else "") +
                          ". See pvTestReport.log in the PowerView Logs folder for details.", level=logging.INFO)
