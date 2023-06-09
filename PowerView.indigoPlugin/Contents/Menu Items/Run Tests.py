
import logging
import os
import sys
from pathlib import PurePath

# sys.path.append(os.path.abspath("../../../../../../../Plugins/PowerView.indigoPlugin/Contents/Server Plugin/pv_tests"))


import pydevd_pycharm
# Debug mode: PDB: 100, PuDB: 101, PyCharm: 102, Debug shell: 200. Use this code in cmdline arg --debug 102
# pydevd_pycharm.settrace('iwsg2.local', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)


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
    log_file_path = (plugin_path + "pyTests.log")
    logging.basicConfig(filename=log_file_path, encoding='utf-8', level=logging.DEBUG)
    logger.error("Run Tests cwd: {}".format(os.getcwd()))
    os.chdir(plugin_path)

    print("Run Tests cwd: {}".format(os.getcwd()))
    logger.error("Run Tests cwd: {}".format(os.getcwd()))

    with add_path(os.path.abspath("./Contents/Server Plugin/pv_tests/")):
        logger.error("Sys.path={}\n\n".format(sys.path))
        import pv_runner  # Will be found now that the folder has been added to the sys.path.

        try:
            pv_runner.run_tests(log_file_path)
        except Exception:
            logger.exception("Run Tests: Tests Failed")

    logger.error("Run Tests: Tests Complete")


# if __name__ == '__main__':
#     logger = logging.getLogger('net.segment7.powerview')
#     logger.error("Run Tests cwd: {}".format(os.getcwd()))
#     run_tests()
