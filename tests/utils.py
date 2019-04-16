from datetime import datetime
from operator import itemgetter
import pytest
import requests


jira_settings = {
    'url': 'https://jira.teko.vn',
    'user': 'lan.nt',
    'password': 'QC12345678',
    'project_key': 'IAM'
}


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
            'name': name,
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


class JiraTest():
    """
    Các Test Suite sẽ kế thừa class này.
    Một Test Suite sẽ bao gồm nhiều Test Cases và Issue tương ứng
        (được định nghĩa qua issue_key).
    Sau khi chạy một Test Suite, kết quả chạy từng Test Cases sẽ được nhóm lại,
        tạo trên Jira thành một Test Cycle.
    Chi tiết luồng:
        - Before each test: Tạo Test Case và gắn với Issue tương ứng.
        - After each test: Đưa kết quả Pass / Fail test tương ứng
            vào biến, sử dụng cho bước sau.
        - After each test suite: Gửi request tạo Test Cycle
            với kết quả của những Test Cases được lấy ở bước trên.
    Ngoài ra, để không tạo duplicate Test case:
        - Before each test suite: Kiểm tra tạo lặp Test Case:
            Chỉ tạo những Test Case mới,
            xóa những Test Case không tìm thấy,
            giữ nguyên những Test Case đã được tạo (cùng tên).
    """
    test_cycle_items = []
    test_services = JiraTestService(jira_settings)

    @pytest.fixture(autouse=True)
    def update_test_result(self, request):
        yield
        self.test_result = 'Pass'
        if request.node.test_outcome.failed:
            self.test_result = 'Fail'

    @pytest.fixture(autouse=True, scope='class')
    def should_submit_test(self, request):
        self.should_submit_test = False
        if self.issue_key and request.config.getoption('--submit-tests'):
            self.should_submit_test = True

    @classmethod
    def setup_class(cls):
        test_keys_list = cls.test_services.get_tests_in_issue(cls.issue_key)
        for test_key in test_keys_list:
            cls.test_services.delete_test(test_key)

    @classmethod
    def teardown_class(cls):
        if cls.should_submit_test:
            cls.test_services.create_test_cycle(cls.issue_key, cls.issue_key,
                                                cls.test_cycle_items)

    def setup_method(self, method):
        self.test_key = self.test_services.create_test(method.__name__,
                                                       self.issue_key)

    def teardown_method(self, method):
        json = {
            'testCaseKey': self.test_key,
            'status': self.test_result
        }
        JiraTest.test_cycle_items.append(json)
