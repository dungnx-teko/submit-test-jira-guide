def pytest_addoption(parser):
    parser.addoption(
        '--submit-tests',
        action='store_true',
        help='Submit tests to Jira'
    )
