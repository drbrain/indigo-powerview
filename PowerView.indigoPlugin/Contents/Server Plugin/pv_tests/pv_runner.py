
import logging
import os
import pytest
import pytest_timestamper as timestamper
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


def run_tests():
    logger = logging.getLogger("net.segment7.powerview")  # net.segment7.powerview
    logger.error(" ")
    logger.error("pv_runner.run_tests: wd={}".format(os.getcwd()))
    logger.debug('pv_runner.run_tests: Starting to run all tests in pv_tests folder.')

    collector = ResultsCollector()
    ret_code = pytest.main(plugins=[collector, timestamper], args=["-v", "-r", "A"])

    logger.debug('pv_runner.run_tests: Finished all tests in pv_tests folder. Results follow:')

    for report in collector.reports:
        logger.debug("id: {} outcome: {}".format(report.nodeid, report.outcome))  # etc
    logger.debug('exit code: {}'.format(collector.exitcode))
    logger.debug('passed: {}, failed: {}, xfailed: {}, skipped: {}'
                 .format(collector.passed, collector.failed, collector.xfailed, collector.skipped))
    logger.debug('total duration: {}'.format(collector.total_duration))
    logger.debug('pytest returned {}.'.format(ret_code))


if __name__ == '__main__':
    run_tests()
