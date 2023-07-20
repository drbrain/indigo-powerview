
import logging
import mock_powerview
import os
import pytest
import time


class ResultsCollector:
    """
    Pytest plugin to collect all results from running tests, and make them available to the caller.

    Sample code that uses the ResultsCollector:

        def run():
            collector = ResultsCollector()
            pytest.main(plugins=[collector])
            for report in collector.reports:
                print('id:', report.nodeid, 'outcome:', report.outcome)  # etc
            print('exit code:', collector.exitcode)
            print('passed:', collector.passed, 'failed:', collector.failed, 'xfailed:', collector.xfailed, 'skipped:', collector.skipped)
            print('total duration:', collector.total_duration)

    """
    def __init__(self):
        self.reports = []
        self.collected = 0
        self.exitcode = 0
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.errored = 0
        self.total_duration = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == 'call':
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        if exitstatus:
            self.exitcode = exitstatus.value
        self.passed = len(terminalreporter.stats.get('passed', []))
        self.failed = len(terminalreporter.stats.get('failed', []))
        self.xfailed = len(terminalreporter.stats.get('xfailed', []))
        self.skipped = len(terminalreporter.stats.get('skipped', []))
        self.errored = len(terminalreporter.stats.get("error", []))

        self.total_duration = time.time() - terminalreporter._sessionstarttime


EXIT_CODE_REASONS = ['All tests were collected and passed successfully',
                     'Tests were collected and run but some of the tests failed',
                     'Test execution was interrupted by the user',
                     'Internal error happened while executing tests',
                     'pytest command line usage error',
                     'No tests were collected'
                     ]
default_hubs = {}


# def __init__():
#     indigo.DEBUG_SERVER_IP = "10.10.28.191"  # IP address of the Mac running PyCharm


def set_default_hubs(hub3, hub2):
    default_hubs["hub3"] = hub3 if hub3 else mock_powerview.LOCAL_IP_V3
    default_hubs["hub2"] = hub2 if hub2 else mock_powerview.LOCAL_IP_V2


def get_default_hubs():
    return default_hubs


def run_tests(hub3, hub2) -> (int, int, int, int):
    logger = logging.getLogger("wsgmac.com.test.powerview")
    wd = os.getcwd()
    logger.debug("pv_runner.run_tests: Starting to run all tests in pv_tests folder. wd={}".format(wd))
    set_default_hubs(hub3, hub2)
    logger.debug(f"pv_runner.run_tests: default_hubs={default_hubs}")

    collector = ResultsCollector()
    ret_code = pytest.main(plugins=[collector], args=["-v", "-raE"])

    logger.debug('pv_runner.run_tests: Finished all tests in pv_tests folder. Results follow:')

    # for report in collector.reports:
    #     logger.debug("id: {} outcome: {}".format(report.nodeid, report.outcome))  # etc
    logger.debug('exit code: {}'.format(collector.exitcode))
    logger.debug('passed: {}, failed: {}, xfailed: {}, skipped: {}'
                 .format(collector.passed, collector.failed, collector.xfailed, collector.skipped))
    logger.debug('total duration: {}'.format(collector.total_duration))
    logger.debug('pytest returned {}={}.'.format(ret_code, EXIT_CODE_REASONS[ret_code]))

    return collector.passed, (collector.failed + collector.xfailed), collector.errored, collector.skipped
