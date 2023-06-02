import logging
import os
import sys
# sys.path.append(os.path.abspath("../../../../../../../Plugins/PowerView.indigoPlugin/Contents/Server Plugin/pv_tests"))


import pydevd_pycharm
pydevd_pycharm.settrace('iwsg2.local', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)


class add_path():
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass


# debug = 102  # Debug mode: PDB: 100, PuDB: 101, PyCharm: 102, Debug shell: 200
#
logger = logging.getLogger('net.segment7.powerview')
os.chdir("../../../../../../../Plugins/PowerView.indigoPlugin/")

logger.error("Run Tests cwd: {}".format(os.getcwd()))

with add_path(os.path.abspath("./Contents/Server Plugin/pv_tests/")):
    logger.error("Sys.path={}\n\n".format(sys.path))
    import pv_runner  # Will be found now that the folder has been added to the sys.path.

    try:
        pv_runner.run_tests()
    except:
        logger.exception("Run Tests: Tests Failed")

logger.error("Run Tests: Tests Complete")
