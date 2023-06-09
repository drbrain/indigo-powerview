
import logging
import os
from pathlib import PurePath
import pytest
import time
import pytest_timestamper as timestamper
import pytester
import pytest_reportlog as rptlog
logger = logging.getLogger("net.segment7.powerview")


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
        print(exitstatus, dir(exitstatus))
        self.exitcode = exitstatus.value
        self.passed = len(terminalreporter.stats.get('passed', []))
        self.failed = len(terminalreporter.stats.get('failed', []))
        self.xfailed = len(terminalreporter.stats.get('xfailed', []))
        self.skipped = len(terminalreporter.stats.get('skipped', []))

        self.total_duration = time.time() - terminalreporter._sessionstarttime


def run_tests(log_file_path):
    logger.error(" ")
    wd = os.getcwd()
    logger.error("pv_runner.run_tests: wd={}".format(wd))
    logger.debug('pv_runner.run_tests: Starting to run all tests in pv_tests folder.')

    collector = ResultsCollector()
    test_details_name = PurePath(os.path.dirname(log_file_path), "pyReport.log")
    ret_code = pytest.main(plugins=[collector, timestamper, rptlog], args=["-v", "-rA", "--capture=fd", "--report-log=" + str(test_details_name)])

    logger.debug('pv_runner.run_tests: Finished all tests in pv_tests folder. Results follow:')

    for report in collector.reports:
        logger.debug("id: {} outcome: {}".format(report.nodeid, report.outcome))  # etc
    logger.debug('exit code: {}'.format(collector.exitcode))
    logger.debug('passed: {}, failed: {}, xfailed: {}, skipped: {}'
                 .format(collector.passed, collector.failed, collector.xfailed, collector.skipped))
    logger.debug('total duration: {}'.format(collector.total_duration))
    logger.debug('pytest returned {}.'.format(ret_code))
