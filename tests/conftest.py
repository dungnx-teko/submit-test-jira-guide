import os
import pytest
import requests


def pytest_addoption(parser):
    parser.addoption(
        '--submit-tests',
        action='store_true',
        help='Submit tests to Jira'
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_pyfunc_call(pyfuncitem):
    outcome = yield

    should_submit_tests = pyfuncitem.config.getoption('--submit-tests')

    if should_submit_tests is False:
        return

    JIRA_PROJECT_KEY = os.environ.get('JIRA_PROJECT_KEY')

    for marker in pyfuncitem.own_markers:
        if marker.name.startswith(JIRA_PROJECT_KEY):
            test_split_name = marker.name.split('_')
            if len(test_split_name) < len(['PROJECTKEY', 'TESTKEY']):
                continue

            JIRA_URL = os.environ.get('JIRA_URL')
            JIRA_USERNAME = os.environ.get('JIRA_USERNAME')
            JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD')
            if not JIRA_URL or \
               not JIRA_PROJECT_KEY or \
               not JIRA_USERNAME or not JIRA_PASSWORD:
                continue

            TEST_CASE_KEY = JIRA_PROJECT_KEY + '-' + test_split_name[1]
            data = {
                'projectKey': JIRA_PROJECT_KEY,
                'testCaseKey': TEST_CASE_KEY
            }

            try:
                outcome.get_result()
                data['status'] = 'Pass'
            except Exception:
                data['status'] = 'Fail'
            finally:
                requests.post(
                    JIRA_URL + '/testresult',
                    auth=(JIRA_USERNAME, JIRA_PASSWORD),
                    json=data
                )
