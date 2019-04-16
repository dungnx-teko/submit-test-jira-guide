import pytest
from .utils import JiraTest
from calculator import simple_plus


class TestSimplePlus(JiraTest):
    issue_key = 'IAM-20'

    def test_should_calculate_plus_correctly(self):
        assert simple_plus(1, 2) == 3

    def test_should_throw_error_when_input_strings(self):
        with pytest.raises(TypeError):
            simple_plus('string', 'string')
