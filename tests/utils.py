import requests


class Jira_Test_Service:
    def __init__(self, jira_settings):
        self.jira_settings = jira_settings
        self.auth_string = (self.jira_settings['user'],
                            self.jira_settings['password'])
        self.url = self.jira_settings['url'] + '/rest/atm/1.0/testcase'

    def get_tests_in_issue(self, issue_key):
        pass

    def create_tests(self, test_name, issue_key):
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
        pass

    def create_test_cycle(self):
        pass
