import pytest


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, 'test_outcome', rep)


def pytest_addoption(parser):
    parser.addoption(
        '--submit-tests',
        action='store_true',
        help='Submit tests to Jira'
    )
