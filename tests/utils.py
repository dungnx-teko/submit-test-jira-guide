from operator import itemgetter
import requests


jira_settings = {
    'url': 'https://jira.teko.vn',
    'user': 'lan.nt',
    'password': 'QC12345678',
    'project_key': 'IAM'
}


class JiraTestService():
    def __init__(self, jira_settings):
        self.project_key = jira_settings['project_key']
        self.auth_string = (jira_settings['user'],
                            jira_settings['password'])
        self.url = jira_settings['url'] + '/rest/atm/1.0/testcase'

    def get_tests_in_issue(self, issue_key):
        params = {
            'query':
            'projectKey = "%s" AND issueKeys IN (%s)' %
            (self.project_key, issue_key)
        }
        response = requests.get(url=self.url + 'search',
                                params=params,
                                auth=self.auth_string).json()
        return list(map(itemgetter('key', response)))

    def create_test(self, test_name, issue_key):
        json = {
            'name': test_name,
            'projectKey': self.jira_settings['projectKey'],
            'issueLinks': [issue_key],
            'status': 'Approved'
        }
        response = requests.post(url=self.url,
                                 json=json,
                                 auth=self.auth_string)
        if response.status_code != 201:
            raise Exception('Create test return with error status code',
                            response.status_code)

        test_key = response.json()['key']
        return test_key

    def delete_test(self, test_key):
        response = requests.delete(url=self.url + test_key,
                                   auth=self.auth_string)
        if response.status_code != 204:
            raise Exception('Delete test return with error status code',
                            response.status_code)

    def create_test_cycle(self):
        pass


class JiraTest():
    test_services = JiraTestService(jira_settings)

    @classmethod
    def setup_class(cls):
        print('Setup class', cls)

    @classmethod
    def teardown_class(cls):
        print('Teardown class', cls)

    def setup_method(self, test_method):
        print('Setup method', test_method)

    def teardown_method(self, test_method):
        print('Teardown method', test_method)
