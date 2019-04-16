import pytest


@pytest.mark.usefixtures('update_test_result', 'jira_test_suite')
class JiraTest:
    pass
