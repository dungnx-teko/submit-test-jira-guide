import pytest
from . import JiraTestService
from calculator import simple_plus


jira_settings = {
    'url': 'https://jira.teko.vn',
    'user': 'lan.nt',
    'password': 'QC12345678',
    'project_key': 'IAM'
}


class TestSimplePlus():
    issue_key = 'IAM-20'
    test_services = JiraTestService(jira_settings)

    @classmethod
    def setup_class(cls):
        print('Setup class', cls)

    @classmethod
    def teardown_class(cls):
        print('Teardown class', cls)

    def setup_method(self, test_method):
        print('Setup method', test_method.name)

    def teardown_method(self, test_method):
        print('Teardown method', test_method)

    def test_should_calculate_plus_correctly(self):
        assert simple_plus(1, 2) == 3
        assert False

    def test_should_throw_error_when_input_strings(self):
        with pytest.raises(TypeError):
            simple_plus('string', 'string')
