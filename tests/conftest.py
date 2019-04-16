from datetime import datetime

import pytest
import requests
from operator import itemgetter


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, 'rep_' + rep.when, rep)


def pytest_addoption(parser):
    parser.addoption(
        '--submit-tests',
        action='store_true',
        help='Submit tests to Jira'
    )


def get_current_time():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


class JiraTestService():
    def __init__(self, jira_settings):
        self.project_key = jira_settings['project_key']
        self.auth_string = (jira_settings['user'],
                            jira_settings['password'])
        self.url = jira_settings['url'] + '/rest/atm/1.0'

    def get_tests_in_issue(self, issue_key):
        params = {
            'query':
            'projectKey = "%s" AND issueKeys IN (%s)' %
            (self.project_key, issue_key)
        }
        response = requests.get(url=self.url + '/testcase/search',
                                params=params,
                                auth=self.auth_string).json()
        return list(map(itemgetter('key'), response))

    def create_test(self, test_name, issue_key):
        json = {
            'name': test_name,
            'projectKey': self.project_key,
            'issueLinks': [issue_key],
            'status': 'Approved'
        }
        response = requests.post(url=self.url + '/testcase',
                                 json=json,
                                 auth=self.auth_string)
        if response.status_code != 201:
            raise Exception('Create test return with error status code',
                            response.status_code)

        test_key = response.json()['key']
        return test_key

    def delete_test(self, test_key):
        response = requests.delete(url=self.url + '/testcase/' + test_key,
                                   auth=self.auth_string)
        if response.status_code != 204:
            raise Exception('Delete test return with error status code',
                            response.status_code)

    def create_test_cycle(self, name, issue_key, items):
        json = {
            'name': name+'-dungnx',
            'projectKey': self.project_key,
            'issueKey': issue_key,
            'plannedStartDate': get_current_time(),
            'plannedEndDate': get_current_time(),
            'items': items
        }
        response = requests.post(url=self.url + '/testrun',
                                 json=json,
                                 auth=self.auth_string)
        if response.status_code != 201:
            raise Exception('Create test cycle return with error status code',
                            response.status_code)


@pytest.fixture(scope='class')
def jira_test_service():
    return JiraTestService({
        'url': 'https://jira.teko.vn',
        'user': 'lan.nt',
        'password': 'QC12345678',
        'project_key': 'IAM'
    })


@pytest.fixture(scope='class')
def jira_test_suite(request, jira_test_service):
    submit_tests = request.config.getoption('--submit-tests', default=False)
    cls = request.cls
    cls.results = {}

    if submit_tests or True:
        test_keys_list = jira_test_service.get_tests_in_issue(cls.issue_key)
        for test_key in test_keys_list:
            jira_test_service.delete_test(test_key)

    yield

    if submit_tests or True:
        # create test keys
        for item in cls.results:
            test_key = jira_test_service.create_test(item, cls.issue_key)
            cls.results[item]['testCaseKey'] = test_key
        test_cycle_items = [v for k, v in cls.results.items()]

        # create test cycle
        jira_test_service.create_test_cycle(cls.issue_key, cls.issue_key, test_cycle_items)


@pytest.fixture()
def update_test_result(request):
    name = request.function.__name__
    request.cls.results[name] = {'status': 'Pass'}
    yield
    if request.node.rep_call.failed:
        request.cls.results[name]['status'] = 'Fail'
